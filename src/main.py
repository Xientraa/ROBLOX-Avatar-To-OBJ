import requests, os.path, json
from os import mkdir
from typing import TypedDict, Any

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(open(SRC_DIR + "/config.json", "r"))


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
            print("[ERROR] Please makesure input is a valid number")
