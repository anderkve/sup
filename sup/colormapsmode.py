# -*- coding: utf-8 -*-
from sup.utils import prettify
from sup.colors import cmaps

def run(args):
    """Prints a list of available colormaps to the console.

    Each colormap is displayed as a series of colored blocks, using the
    `prettify` function from `sup.utils` and the `cmaps` list from
    `sup.colors`. The colormaps are indexed and presented with their
    corresponding number.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
            This function does not currently use any arguments from `args`.

    Returns:
        None
    """

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
