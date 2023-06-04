from typing import Optional


class Vector:
    def __init__(
        self,
        x: Optional[float] = 0.0,
        y: Optional[float] = 0.0,
        z: Optional[float] = 0.0,
        w: Optional[float] = 1.0,
    ) -> None:
        self.x = x or 0.0
        self.y = y or 0.0
        self.z = z or 0.0
        self.w = w or 1.0

    @staticmethod
    def fromString(vectorString: str) -> "Vector":
        splitVectorString = vectorString.split(" ")
        return Vector(
            float(splitVectorString[0]) if len(splitVectorString) >= 1 else 0.0,
            float(splitVectorString[1]) if len(splitVectorString) >= 2 else 0.0,
            float(splitVectorString[2]) if len(splitVectorString) >= 3 else 0.0,
            float(splitVectorString[3]) if len(splitVectorString) >= 4 else 1.0,
        )

    def applyOffset(self, offsetVector: "Vector") -> None:
        self.x += offsetVector.x
        self.y += offsetVector.y
        self.z += offsetVector.z
        self.w += offsetVector.w

    def __str__(self):
        return f"{self.x} {self.y} {self.z}" + (
            f" {str(self.w)}" if self.w != 1 else ""
        )


def unplugAlphaMapFromMTL(filePath: str) -> None:
    lines = open(filePath, "r").readlines()
    for index, line in enumerate(lines):
        if line.startswith("map_d "):
            lines[index] = f"# {line}"
        lines[index] = lines[index].strip()
    open(filePath, "w").write("\n".join(lines))


def offsetObjVertices(filePath: str, offsetVector: Vector) -> None:
    lines = open(filePath, "r").readlines()
    for index, line in enumerate(lines):
        if line.startswith("v "):
            lineVector = Vector.fromString(vectorString=line[2:].strip())
            lineVector.applyOffset(offsetVector)
            lines[index] = f"v {str(lineVector)}"
        else:
            lines[index] = line.strip()
    open(filePath, "w").write("\n".join(lines))
