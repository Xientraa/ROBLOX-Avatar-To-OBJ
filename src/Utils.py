def isStringInt(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False
