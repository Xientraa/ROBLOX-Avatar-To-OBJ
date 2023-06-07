from typing import TypedDict


class AvatarRenderResponse(TypedDict):
    targetId: int
    state: str
    imageUrl: str
