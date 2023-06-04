import requests, time
from typing import TypedDict, Any, Literal
from RobloSecurity import RobloSecurityCookie
from bodyColors import convertAvatarInformationBodyColorIdsToHex


class Hash:
    def __init__(self, hash: str) -> None:
        self.hash = hash


class CdnUrl:
    def __init__(self, url: str) -> None:
        self.url = url


class ModelData(TypedDict):
    camera: Any
    aabb: Any
    mtl: str
    obj: str
    textures: list[str]


def getModelInformationFromUrl(url: CdnUrl) -> ModelData:
    r = requests.get(url.url)
    if r.status_code == 200:
        json: ModelData = r.json()
        return json
    raise requests.HTTPError


def getCdnUrlFromHash(hash: Hash) -> CdnUrl:
    st = 31
    for i in range(0, 32):
        st ^= ord(hash.hash[i])
    return CdnUrl(f"https://t{st % 8}.rbxcdn.com/{hash.hash}")


def downloadFileFromHash(hash: Hash, filePath: str) -> None:
    r = requests.get(getCdnUrlFromHash(hash).url)
    if r.status_code == 200:
        open(filePath, "wb").write(r.content)
        return
    raise requests.HTTPError


def getAvatarFileHashesFromUrl(url: str) -> ModelData:
    r = requests.get(url)
    if r.status_code == 200:
        json: ModelData = r.json()
        return json
    raise requests.HTTPError


def generateCharacterModelCdnUrl(
    avatarInformation: dict[str, Any],
    cookie: RobloSecurityCookie,
    avatarType: Literal["R6", "R15"],
    useDefaultScale: bool,
) -> CdnUrl:
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
                    "bodyColors": convertAvatarInformationBodyColorIdsToHex(
                        avatarInformation["bodyColors"]
                    ),
                    "scales": (
                        (
                            {
                                "height": 1,
                                "width": 1,
                                "head": 1,
                                "depth": 1,
                                "proportion": 0,
                                "bodyType": 0,
                            }
                            if useDefaultScale
                            else avatarInformation["scales"]
                        )
                    ),
                    "playerAvatarType": {"playerAvatarType": avatarType},
                },
            },
            headers={"x-csrf-token": cookie.xCSRFToken},
            cookies={".ROBLOSECURITY": cookie.cookie},
        )

        match r.status_code:
            case 200:
                json = r.json()
                if json["state"] == "Completed":
                    return CdnUrl(json["imageUrl"])
                time.sleep(1)
            case 403:
                cookie.refreshXCSRFToken()
            case 429:
                raise requests.HTTPError("Too many requests!")
            case _:
                print(r.status_code)
                raise requests.HTTPError()
