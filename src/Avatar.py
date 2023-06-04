import requests
from typing import Any, Literal
from RobloSecurity import RobloSecurityCookie
from Cdn import (
    downloadFileFromHash,
    Hash,
    getModelInformationFromUrl,
    generateCharacterModelCdnUrl,
)
from Model import Vector, offsetObjVertices, unplugAlphaMapFromMTL
from os import mkdir


class UserDoesNotExist(Exception):
    def __init__(self) -> None:
        pass


def getAvatarInformation(userId: int) -> dict[str, Any]:
    r = requests.get(f"https://avatar.roblox.com/v1/users/{userId}/avatar")
    if r.status_code == 400:
        raise UserDoesNotExist
    return r.json()


def downloadAvatarFromUserId(
    userId: int,
    downloadPath: str,
    cookie: RobloSecurityCookie,
    avatarType: Literal["R6", "R15"],
    useDefaultScale: bool,
) -> None:
    avatarInformation = getAvatarInformation(userId)
    modelInformation = getModelInformationFromUrl(
        generateCharacterModelCdnUrl(
            avatarInformation, cookie, avatarType, useDefaultScale
        )
    )

    downloadPath = f'{downloadPath}/{modelInformation["obj"]}'
    try:
        mkdir(downloadPath)
    except:
        pass

    downloadFileFromHash(
        Hash(modelInformation["obj"]), f'{downloadPath}/{modelInformation["obj"]}.obj'
    )
    downloadFileFromHash(
        Hash(modelInformation["mtl"]), f'{downloadPath}/{modelInformation["obj"]}.mtl'
    )

    offsetObjVertices(
        f'{downloadPath}/{modelInformation["obj"]}.obj',
        Vector(0, -modelInformation["aabb"]["min"]["y"], 0, 0),
    )
    unplugAlphaMapFromMTL(f'{downloadPath}/{modelInformation["obj"]}.mtl')

    materialFileContents = open(
        f'{downloadPath}/{modelInformation["obj"]}.mtl', "r"
    ).read()
    for hashString in modelInformation["textures"]:
        materialFileContents = materialFileContents.replace(
            hashString, f"{hashString}.png"
        )
        downloadFileFromHash(Hash(hashString), f"{downloadPath}/{hashString}.png")

    open(f'{downloadPath}/{modelInformation["obj"]}.mtl', "w").write(
        materialFileContents
    )
