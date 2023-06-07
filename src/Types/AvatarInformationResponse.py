from typing import Optional, List, Any, TypedDict


class AssetType(TypedDict):
    id: int
    name: str


class Meta(TypedDict):
    order: int
    version: int


class Asset(TypedDict):
    id: int
    name: str
    assetType: AssetType
    currentVersionId: int
    meta: Optional[Meta]


class BodyColors(TypedDict):
    headColorId: int
    torsoColorId: int
    rightArmColorId: int
    leftArmColorId: int
    rightLegColorId: int
    leftLegColorId: int


class Scales(TypedDict):
    height: int
    width: int
    head: int
    depth: int
    proportion: int
    bodyType: int


class AvatarInformationResponse(TypedDict):
    scales: Scales
    playerAvatarType: str
    bodyColors: BodyColors
    assets: List[Asset]
    defaultShirtApplied: bool
    defaultPantsApplied: bool
    emotes: List[Any]
