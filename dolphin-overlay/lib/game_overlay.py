import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Self

from PIL import Image
import av

from . import types


class GameOverlayData:
    data: list[dict]

    def __init__(self, data: list[dict]):
        self.data = data

    @classmethod
    def load_from_csv(cls, csv_filepath: str | Path) -> Self:
        with open(csv_filepath, "r") as f:
            csv_data = list(csv.DictReader(f))
        return cls(data=csv_data)


@dataclass
class GameOverlayDefaults:
    component_background_color: types.Color
    font_name: str
    font_size: int
    font_color: types.Color
    font_stroke_width: int
    font_stroke_fill: types.Color
    font_monospace_gap: int
    main_line_color: types.Color
    main_line_width: int
    outline_width: int
    outline_color: types.Color
    positive_color: types.Color
    negative_color: types.Color


class GameOverlayComponent(Protocol):
    def apply_defaults(self, defaults: GameOverlayDefaults) -> None:
        pass

    def pre_draw(self, image: Image.Image) -> None:
        pass

    def draw(self, image: Image.Image, game_data: dict) -> None:
        pass


class GameOverlay:
    def __init__(
        self,
        components: list[GameOverlayComponent],
        resolution: types.Vec2,
        game_feed_box: tuple[int, int, int, int],
        defaults: GameOverlayDefaults,
    ) -> None:
        self._components = components
        self._resolution = resolution
        self._game_feed_box = game_feed_box
        for component in self._components:
            component.apply_defaults(defaults)

    def _pre_draw(self, overlay_img: Image.Image):
        for component in self._components:
            component.pre_draw(overlay_img)

    def _draw(self, overlay_img: Image.Image, game_data: dict):
        for component in self._components:
            component.draw(overlay_img, game_data)

    def _draw_composite_image(
        self, game_feed_img: Image.Image, overlay_img: Image.Image
    ) -> Image.Image:
        composite_img = Image.new("RGBA", self._resolution)
        resized_game_img = game_feed_img
        target_game_feed_size = (
            self._game_feed_box[2] - self._game_feed_box[0],
            self._game_feed_box[3] - self._game_feed_box[1],
        )
        if game_feed_img.size != target_game_feed_size:
            # TODO: probably more efficient to do this in the whole video first
            resized_game_img = game_feed_img.resize(target_game_feed_size)
        composite_img.paste(resized_game_img, box=self._game_feed_box)
        composite_img.paste(overlay_img, mask=overlay_img)
        return composite_img

    def draw_single_frame(
        self,
        frame_number: int,
        game_overlay_data: GameOverlayData,
        game_feed_video_filepath: str | Path,
    ) -> Image.Image:
        game_feed_container = av.open(game_feed_video_filepath, "r")
        game_feed_frame = None
        for frame in game_feed_container.decode(video=0):
            if frame.pts and frame.pts > frame_number:
                game_feed_frame = frame
                break
        if game_feed_frame is None:
            raise ValueError(f"Frame {frame_number} does not exist in video")
        game_feed_img = game_feed_frame.to_image()
        overlay_img = Image.new("RGBA", self._resolution, color=(0, 0, 0, 0))
        self._pre_draw(overlay_img)
        assert game_feed_frame.pts is not None
        overlay_frame = max(0, game_feed_frame.pts - 1)
        self._draw(overlay_img, game_overlay_data.data[overlay_frame])
        return self._draw_composite_image(game_feed_img, overlay_img)

    def encode_all_frames(
        self,
        video_output_path: str | Path,
        game_overlay_data: GameOverlayData,
        game_feed_video_filepath: str | Path,
    ) -> None:
        game_feed_video = av.open(game_feed_video_filepath, "r")
        output_video = av.open(video_output_path, "w")
        output_stream = output_video.add_stream(
            "h264", game_feed_video.streams.video[0].base_rate
        )
        output_stream.width = self._resolution[0]
        output_stream.height = self._resolution[1]
        base_img = Image.new("RGBA", self._resolution, color=(0, 0, 0, 0))
        self._pre_draw(base_img)
        for game_feed_frame in game_feed_video.decode(video=0):
            overlay_img = base_img.copy()
            assert game_feed_frame.pts is not None
            overlay_frame = max(0, game_feed_frame.pts - 1)
            # TODO: the overlay_frame as is might not work for multiple files; rework
            # this
            self._draw(overlay_img, game_overlay_data.data[overlay_frame])
            composite_img = self._draw_composite_image(
                game_feed_frame.to_image(), overlay_img
            )
            output_frame: av.VideoFrame = av.VideoFrame.from_image(composite_img)
            output_frame.pts = game_feed_frame.pts
            output_packet = output_stream.encode(output_frame)
            output_video.mux(output_packet)
        output_packet = output_stream.encode(None)
        output_video.mux(output_packet)
        output_video.close()
        game_feed_video.close()
