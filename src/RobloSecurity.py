import requests


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
