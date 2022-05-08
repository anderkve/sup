from sup.utils import prettify
from sup.colors import cmaps

def run(args):

    print("Available colormaps")
    print("-------------------")
    print()

    for i, ccodes in enumerate(cmaps):

        colors = str(i) + ") "

        for ccode in ccodes:
            colors += prettify("██████", ccode, 232)
        colors += "\n"

        print(colors)

    return
