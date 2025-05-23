# -*- coding: utf-8 -*-
from sup.utils import prettify

def run(args):
    """Prints a table of all 256 available terminal colors to the console.

    Each color is displayed as a block with its corresponding color code.
    The `prettify` function from `sup.utils` is used for formatting
    each color block, showing the color code itself on a background of
    that color. The colors are arranged in a grid.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
            This function does not currently use any arguments from `args`.

    Returns:
        None
    """

    print("Available colors")
    print("----------------")
    colors = ""
    for i in range(256):
        colors += prettify(" {:^5} ".format(i), 232, i)
        colors += " "
        if (i+1) % 8 == 0:
            colors += "\n"
    print(colors)

    return
