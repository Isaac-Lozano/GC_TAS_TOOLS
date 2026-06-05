# dolphin-overlay

This is a tool to render a memory and input viewer overlay on top of a game feed from a
TAS movie created from Dolphin Emulator. This is primarily created for using with Sonic
Adventure 2: Battle.

## Installing requirements

Install the requirements in your system-wide Python installation:
```
pip install -r requirements.txt
```

Or optionally create a virtual environment for the project and install the requirements
there:
```
python -m venv .env
.\.env\Scripts\activate
pip install -r requirements.txt
```

## Using the tool

Move both your .avi or .mp4 framedump and the .csv variables dump to the `input/`
folder. Both files should have the same base name, e.g.:
```text
input
├──dark_story.avi
└──dark_story.csv
```

### Render a single frame

You can start by rendering a single frame to ensure the setup is correct:
```sh
python create_single_frame.py [base_filename] [frame_number]
```

For example:
```sh
python create_single_frame.py dark_story 500
```
Renders the 500th frame of the `dark_story` movie with the overlay and saves it at
`output/dark_story_frame_000500.png`.

### Rendering the full movie

Finally, render the full movie with:

```sh
python create_overlay.py [base_filename]
```

For example:
```sh
python create_overlay.py dark_story
```
Renders the full overlay of the `dark_story` movie and saves it at
`output/dark_story_overlay.mp4`.

