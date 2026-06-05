from dataclasses import dataclass
import math


@dataclass
class Vector:
    x: float
    y: float
    z: float

    def rotate(self, r):
        x = (
            self.x
            * (
                math.cos(r.z) * math.cos(r.y)
                + math.sin(r.z) * math.sin(r.x) * math.sin(r.y)
            )
            + self.y * (-math.cos(r.x) * math.sin(r.z))
            + self.z
            * (
                -math.cos(r.z) * math.sin(r.y)
                + math.cos(r.y) * math.sin(r.z) * math.sin(r.x)
            )
        )
        y = (
            self.x
            * (
                math.cos(r.y) * math.sin(r.z)
                - math.cos(r.z) * math.sin(r.x) * math.sin(r.y)
            )
            + self.y * (math.cos(r.z) * math.cos(r.x))
            + self.z
            * (
                -math.sin(r.z) * math.sin(r.y)
                - math.cos(r.z) * math.cos(r.y) * math.sin(r.x)
            )
        )
        z = (
            self.x * (math.cos(r.x) * math.sin(r.y))
            + self.y * (math.sin(r.x))
            + self.z * (math.cos(r.x) * math.cos(r.y))
        )
        return Vector(x, y, z)

    def cross(self, o):
        x = self.y * o.z - self.z * o.y
        y = self.z * o.x - self.x * o.z
        z = self.x * o.y - self.y * o.x
        return Vector(x, y, z)

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z


@dataclass
class Rotation:
    x: float
    y: float
    z: float

    @classmethod
    def from_bcd(cls, x, y, z):
        return cls(bcd_to_rad(x), bcd_to_rad(y), bcd_to_rad(z))


def bcd_to_rad(bcd):
    return bcd * math.tau / 2**16


def bcd_to_signed_bcd(bcd):
    return (bcd + 32768) % 65536 - 32768
