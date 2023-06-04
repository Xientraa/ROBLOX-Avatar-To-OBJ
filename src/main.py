import requests, os.path, json
from os import mkdir
from typing import TypedDict, Any, Optional

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(open(SRC_DIR + "/config.json", "r"))


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


class AvatarInformation(TypedDict):
    camera: Any
    aabb: Any
    mtl: str
    obj: str
    textures: list[str]


def getCdnUrlFromHash(hash: str) -> str:
    st = 31
    for i in range(0, 32):
        st ^= ord(hash[i])
    return f"https://t{st % 8}.rbxcdn.com/{hash}"


def getAvatarImageUrl(userId: int) -> str:
    r = requests.get(
        f"https://thumbnails.roblox.com/v1/users/avatar-3d?userId={userId}"
    )
    if r.status_code == 200:
        return r.json()["imageUrl"]
    raise requests.HTTPError


def getAvatarInformation(userId: int) -> AvatarInformation:
    url = getAvatarImageUrl(userId)
    r = requests.get(url)
    if r.status_code == 200:
        json: AvatarInformation = r.json()
        return json
    raise requests.HTTPError


def downloadFileFromHash(hash: str, filePath: str) -> None:
    r = requests.get(getCdnUrlFromHash(hash))
    if r.status_code == 200:
        open(filePath, "wb").write(r.content)
        return
    raise requests.HTTPError


def offsetAvatarOBJ(filePath: str, offsetVector: Vector) -> None:
    lines = open(filePath, "r").readlines()
    for index, line in enumerate(lines):
        if line.startswith("v "):
            lineVector = Vector.fromString(vectorString=line[2:].strip())
            lineVector.applyOffset(offsetVector)
            lines[index] = f"v {str(lineVector)}"
        else:
            lines[index] = line.strip()
    open(filePath, "w").write("\n".join(lines))


def downloadAvatar(userId: int, downloadPath: str) -> None:
    avatarInformation = getAvatarInformation(userId)
    downloadPath = f'{downloadPath}/{avatarInformation["obj"]}'
    try:
        mkdir(downloadPath)
    except:
        pass

    downloadFileFromHash(
        avatarInformation["obj"], f'{downloadPath}/{avatarInformation["obj"]}.obj'
    )
    downloadFileFromHash(
        avatarInformation["mtl"], f'{downloadPath}/{avatarInformation["obj"]}.mtl'
    )

    offsetAvatarOBJ(
        f'{downloadPath}/{avatarInformation["obj"]}.obj', Vector(0, -101.02916, 0, 0)
    )

    materialFileContents = open(
        f'{downloadPath}/{avatarInformation["obj"]}.mtl', "r"
    ).read()
    for hash in avatarInformation["textures"]:
        materialFileContents = materialFileContents.replace(hash, f"{hash}.png")
        downloadFileFromHash(hash, f"{downloadPath}/{hash}.png")

    open(f'{downloadPath}/{avatarInformation["obj"]}.mtl', "w").write(
        materialFileContents
    )


if __name__ == "__main__":
    while True:
        inputString = input("UserID >> ")
        try:
            userId = int(inputString)
            print(f"[INFO] Downloading userId: {userId}")
            downloadAvatar(userId, CONFIG["DownloadDirectory"])
        except ValueError:
            print("[ERROR] Please make sure input is a valid number")
