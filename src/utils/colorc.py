class bcolors:
    END = "0"
    BOLD = "1"
    ITALIC = "3"
    URL = "4"
    BLINK = "5"
    BLINK2 = "6"
    SELECTED = "7"
    BLACK = "30"
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    VIOLET = "35"
    BEIGE = "36"
    WHITE = "37"
    GREY = "90"
    RED2 = "91"
    GREEN2 = "92"
    YELLOW2 = "93"
    BLUE2 = "94"
    VIOLET2 = "95"
    BEIGE2 = "96"
    WHITE2 = "97"
    BGBLACK = "40"
    BGRED = "41"
    BGGREEN = "42"
    BGYELLOW = "43"
    BGBLUE = "44"
    BGVIOLET = "45"
    BGBEIGE = "46"
    BGWHITE = "47"
    BGGREY = "100"
    BGRED2 = "101"
    BGGREEN2 = "102"
    BGYELLOW2 = "103"
    BGBLUE2 = "104"
    BGVIOLET2 = "105"
    BGBEIGE2 = "106"
    BGWHITE2 = "107"

class cc:
    use_verbose: bool = True

    def disable_verbose():
        cc.use_verbose = False

    def error(msg: str):
        print(f"\033[{bcolors.BGRED};{bcolors.BLACK}m ERROR \033[0m {msg}")


    def info(msg: str):
        print(f"\033[{bcolors.BGBLUE};{bcolors.BLACK}m INFO \033[0m {msg}")


    def warn(msg: str):
        print(f"\033[{bcolors.BGYELLOW};{bcolors.BLACK}m WARN \033[0m {msg}")

    def verbose(msg: str):
        if cc.use_verbose:
            print(f"\033[{bcolors.BGBLUE};{bcolors.BLACK}m VERB \033[0m {msg}")
    
    def label(label: str, info: str):
        print(f"\033[{bcolors.BLUE2}m * {label}: \033[0m {info}")
