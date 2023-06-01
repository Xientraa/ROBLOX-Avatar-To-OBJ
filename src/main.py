import requests
from typing import TypedDict, Any, Optional


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


def downloadFileFromHash(
    hash: str, fileExtension: str, fileName: Optional[str] = None
) -> None:
    r = requests.get(getCdnUrlFromHash(hash))
    if r.status_code == 200:
        open(f"./{fileName or hash}.{fileExtension}", "wb").write(r.content)
        return
    raise requests.HTTPError


def downloadAvatar(userId: int) -> None:
    avatarInformation = getAvatarInformation(userId)
    downloadFileFromHash(avatarInformation["obj"], "obj", avatarInformation["obj"])
    downloadFileFromHash(avatarInformation["mtl"], "mtl", avatarInformation["obj"])
    materialFileContents = open(f'./{avatarInformation["obj"]}.mtl', "r").read()
    for hash in avatarInformation["textures"]:
        materialFileContents = materialFileContents.replace(hash, f"{hash}.png")
        downloadFileFromHash(hash, "png", hash)
    open(f'./{avatarInformation["obj"]}.mtl', "w").write(materialFileContents)
