import requests
from typing import TypedDict, Any


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
