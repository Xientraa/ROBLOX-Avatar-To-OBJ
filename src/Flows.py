from typing import Literal
from Utils import isStringInt


def avatarTypeFlow() -> Literal["R6", "R15"]:
    print("Select an avatar type: 1) R6 2) R15")
    while True:
        inputString = input(">> ")
        if isStringInt(inputString) and int(inputString) in [1, 2]:
            return "R6" if inputString == "1" else "R15"
        else:
            print("[ERROR] Please make sure input is a valid number")


def userIdFlow() -> int:
    print("Enter a ROBLOX user id.")
    while True:
        inputString = input(">> ")
        if isStringInt(inputString):
            return int(inputString)
        else:
            print("[ERROR] Please make sure input is a valid number")


def useAvatarScalesFlow() -> bool:
    print("Use avatar scales (y/n)")
    while True:
        inputString = input(">> ").lower()
        if inputString in ["y", "n"]:
            return True if inputString == "y" else False
        else:
            print("[ERROR] Please make sure input is either y or n")
