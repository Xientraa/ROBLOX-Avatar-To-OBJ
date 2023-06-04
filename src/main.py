import requests, os.path, json
from os import mkdir
from typing import TypedDict, Any, Optional, Literal
from time import sleep

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(
    open(SRC_DIR + "/secret.config.json")
    if os.path.exists(SRC_DIR + "/secret.config.json")
    else open(SRC_DIR + "/config.json", "r")
)


class RobloSecurityCookie:
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie
        self.xCSRFToken = ""

        if RobloSecurityCookie.isRobloSecurityCookieDead(self.cookie):
            raise Exception("ROBLOSECURITY cookie is dead.")
        self.refreshXCSRFToken()

    @staticmethod
    def isRobloSecurityCookieDead(cookie: str) -> bool:
        return (
            requests.get(
                "https://users.roblox.com/v1/users/authenticated",
                cookies={".ROBLOSECURITY": cookie},
            ).status_code
            == 401
        )

    def refreshXCSRFToken(self) -> str:
        r = requests.post(
            "https://auth.roblox.com/v2/logout", cookies={".ROBLOSECURITY": self.cookie}
        )
        token = r.headers.get("x-csrf-token")
        if token == None:
            raise Exception("Unable to retrieve x-csrf-token")
        self.xCSRFToken = token
        return token


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


class ModelData(TypedDict):
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


def getAvatarFileHashesFromUrl(url: str) -> ModelData:
    r = requests.get(url)
    if r.status_code == 200:
        json: ModelData = r.json()
        return json
    raise requests.HTTPError


def downloadFileFromHash(hash: str, filePath: str) -> None:
    r = requests.get(getCdnUrlFromHash(hash))
    if r.status_code == 200:
        open(filePath, "wb").write(r.content)
        return
    raise requests.HTTPError


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


def getAvatarInformation(userId: int) -> dict[str, Any]:
    r = requests.get(f"https://avatar.roblox.com/v1/users/{userId}/avatar")
    if r.status_code == 400:
        raise Exception("User doesn't exist!")
    return r.json()


def generateCharacterModelCdnUrl(
    avatarInformation: dict[str, Any],
    cookie: RobloSecurityCookie,
    avatarType: Literal["R6", "R15"],
    scales: Optional[dict[str, int]] = None,
) -> str:
    while True:
        r = requests.post(
            "https://avatar.roblox.com/v1/avatar/render",
            json={
                "thumbnailConfig": {
                    "thumbnailId": 3,
                    "thumbnailType": "3d",
                    "size": "420x420",
                },
                "avatarDefinition": {
                    "assets": [
                        {
                            "id": asset["id"],
                            "meta": asset["meta"] if asset.get("meta") else None,
                        }
                        for asset in avatarInformation["assets"]
                    ],
                    "bodyColors": {
                        "headColor": "#CC8E69",
                        "leftArmColor": "#CC8E69",
                        "leftLegColor": "#CC8E69",
                        "rightArmColor": "#CC8E69",
                        "rightLegColor": "#CC8E69",
                        "torsoColor": "#CC8E69",
                    },
                    "scales": (
                        scales
                        or {
                            "height": 1,
                            "width": 1,
                            "head": 1,
                            "depth": 1,
                            "proportion": 0,
                            "bodyType": 0,
                        }
                    ),
                    "playerAvatarType": {"playerAvatarType": avatarType},
                },
            },
            headers={"x-csrf-token": cookie.xCSRFToken},
            cookies={".ROBLOSECURITY": cookie.cookie},
        )

        if r.status_code == 200:
            json = r.json()
            if json["state"] == "Completed":
                return json["imageUrl"]
            sleep(1)
        elif r.status_code == 403:
            cookie.refreshXCSRFToken()


def downloadAvatarFromUserId(
    userId: int, downloadPath: str, cookie: RobloSecurityCookie
) -> None:
    avatarInformation = getAvatarInformation(userId)
    avatarFileHashes = getAvatarFileHashesFromUrl(
        generateCharacterModelCdnUrl(avatarInformation, cookie, "R6")
    )

    downloadPath = f'{downloadPath}/{avatarFileHashes["obj"]}'
    try:
        mkdir(downloadPath)
    except:
        pass

    downloadFileFromHash(
        avatarFileHashes["obj"], f'{downloadPath}/{avatarFileHashes["obj"]}.obj'
    )
    downloadFileFromHash(
        avatarFileHashes["mtl"], f'{downloadPath}/{avatarFileHashes["obj"]}.mtl'
    )

    offsetObjVertices(
        f'{downloadPath}/{avatarFileHashes["obj"]}.obj', Vector(0, -101.02916, 0, 0)
    )
    unplugAlphaMapFromMTL(f'{downloadPath}/{avatarFileHashes["obj"]}.mtl')

    materialFileContents = open(
        f'{downloadPath}/{avatarFileHashes["obj"]}.mtl', "r"
    ).read()
    for hash in avatarFileHashes["textures"]:
        materialFileContents = materialFileContents.replace(hash, f"{hash}.png")
        downloadFileFromHash(hash, f"{downloadPath}/{hash}.png")

    open(f'{downloadPath}/{avatarFileHashes["obj"]}.mtl', "w").write(
        materialFileContents
    )


if __name__ == "__main__":
    cookie = RobloSecurityCookie(CONFIG["Cookie"])

    while True:
        inputString = input("UserID >> ")
        try:
            userId = int(inputString)
            print(f"[INFO] Downloading userId: {userId}")
            downloadAvatarFromUserId(userId, CONFIG["DownloadDirectory"], cookie)
        except ValueError:
            print("[ERROR] Please make sure input is a valid number")
