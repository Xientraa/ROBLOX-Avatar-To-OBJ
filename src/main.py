import os.path, json
from RobloSecurity import RobloSecurityCookie
from Avatar import downloadAvatarFromUserId
from Flows import userIdFlow, avatarTypeFlow, useDefaultAvatarScalesFlow


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(
    open(SRC_DIR + "/secret.config.json")
    if os.path.exists(SRC_DIR + "/secret.config.json")
    else open(SRC_DIR + "/config.json", "r")
)


if __name__ == "__main__":
    cookie = RobloSecurityCookie(CONFIG["Cookie"])

    while True:
        userId = userIdFlow()
        avatarType = avatarTypeFlow()
        if avatarType == "R15":
            useDefaultAvatarScales = useDefaultAvatarScalesFlow()
        else:
            useDefaultAvatarScales = True
        print(f"[INFO] Downloading userId: {userId}")
        downloadAvatarFromUserId(
            userId,
            CONFIG["DownloadDirectory"],
            cookie,
            avatarType,
            useDefaultAvatarScales,
        )
