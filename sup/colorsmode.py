# -*- coding: utf-8 -*-
from sup.utils import prettify

def run(args):

    print("Available colors")
    print("----------------")
    colors = ""
    for i in range(256):
        colors += prettify(" {:^5} ".format(i), 232, i)
        colors += " "
        # if (i > 0) and (i % 8) == 0:
        if ((i+1) % 8) == 0:
            colors += "\n"
    print(colors)

    return
