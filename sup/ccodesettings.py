# -*- coding: utf-8 -*-
import numpy as np
import sup.defaults as defaults

class CCodeSettings:
    """A class to contain color codes settings.

    For the attributes below, all the dictionaries have four entries, 
    corresponding to the four possible combinations of black/white 
    background and color/grayscale plot. The four dictionary keys are 
    "color_bb", "color_wb", "grayscale_bb" and "grayscale_wb".

    Attributes:
        bg_ccodes (dict of str: int): Background color codes.

        fg_ccodes (dict of str: int): Foreground color codes.

        empty_bin_ccodes (dict of str: int): Color codes for empyt bins.

        fill_bin_ccodes (dict of str: int): Color codes for "fill bins".

        max_bin_ccodes (dict of str: int): Color codes for the bin(s)
            with the maximum z value.

        graph_ccodes (dict of str: int): Color codes for 1d graphs.

        bar_ccodes_lists (dict of lists of ints): Lists of color codes
            for drawing horizontal bars (e.g. CR/CI bars) below plots. 

        cmaps (dict of lists of ints): Color maps in the form of lists
            of color codes.

        bg_ccode (int): Current background color code.

        fg_ccode (int): Current foreground color code.

        empty_bin_ccode (int): Current color code for empty bins.

        fill_bin_ccode (int): Current color code for fill bins.

        max_bin_ccode (int): Current color code for the max-z bin.

        graph_ccode (int): Current color code for 1d graphs.

        bar_ccodes (list of ints): Current color codes for horizontal 
            bars below plots.

        ccodes (list of ints): Current color map.  

        use_white_bg (bool): Draw plot on a white bakground?

        use_grayscale (bool): Draw plot in grayscale?

        use_n_colors (int): Current number of color map colors to use.

    Methods:
        update(): Make sure the current settings are consistent.

    """

    def __init__(self):
        """Constructor."""

        self.bg_ccodes = {
            "color_bb" : defaults.bg_ccode_bb,
            "color_wb" : defaults.bg_ccode_wb,
            "grayscale_bb" : defaults.bg_ccode_bb,
            "grayscale_wb" : defaults.bg_ccode_wb,
        }

        self.fg_ccodes = {
            "color_bb" : defaults.fg_ccode_bb,
            "color_wb" : defaults.fg_ccode_wb,
            "grayscale_bb" : defaults.fg_ccode_bb,
            "grayscale_wb" : defaults.fg_ccode_wb,
        }

        self.empty_bin_ccodes = {
            "color_bb" : defaults.empty_bin_ccode_color_bb,
            "color_wb" : defaults.empty_bin_ccode_color_wb,
            "grayscale_bb" : defaults.empty_bin_ccode_grayscale_bb,
            "grayscale_wb" : defaults.empty_bin_ccode_grayscale_wb,
        }

        self.fill_bin_ccodes = {
            "color_bb" : defaults.fill_bin_ccode_color_bb,
            "color_wb" : defaults.fill_bin_ccode_color_wb,
            "grayscale_bb" : defaults.fill_bin_ccode_grayscale_bb,
            "grayscale_wb" : defaults.fill_bin_ccode_grayscale_wb,
        }

        self.max_bin_ccodes = {
            "color_bb" : defaults.max_bin_ccode_color_bb,
            "color_wb" : defaults.max_bin_ccode_color_wb,
            "grayscale_bb" : defaults.max_bin_ccode_grayscale_bb,
            "grayscale_wb" : defaults.max_bin_ccode_grayscale_wb,
        }

        self.graph_ccodes = {
            "color_bb" : defaults.graph_ccode_color_bb,
            "color_wb" : defaults.graph_ccode_color_wb,
            "grayscale_bb" : defaults.graph_ccode_grayscale_bb,
            "grayscale_wb" : defaults.graph_ccode_grayscale_wb,
        }

        self.bar_ccodes_lists = {
            "color_bb" : defaults.bar_ccodes_color,
            "color_wb" : defaults.bar_ccodes_color,
            "grayscale_bb" : defaults.bar_ccodes_grayscale,
            "grayscale_wb" : defaults.bar_ccodes_grayscale,
        }

        self.cmaps = {
            "color_bb" : defaults.cmap_color_bb,
            "color_wb" : defaults.cmap_color_wb,
            "grayscale_bb" : defaults.cmap_grayscale_bb,
            "grayscale_wb" : defaults.cmap_grayscale_wb,
        }

        self.bg_ccode = None
        self.fg_ccode = None
        self.empty_bin_ccode = None 
        self.fill_bin_ccode = None
        self.max_bin_ccode = None
        self.graph_ccode = None
        self.bar_ccodes = None
        self.ccodes = None
        self.use_white_bg = False
        self.use_grayscale = False
        self.use_n_colors = len(self.cmaps["color_bb"])

        self.update()



    def update(self):
        """Make sure the current settings are consistent."""  

        use_setting = ""
        if not self.use_white_bg and not self.use_grayscale:
            use_setting = "color_bb"
        elif self.use_white_bg and not self.use_grayscale:
            use_setting = "color_wb"
        elif not self.use_white_bg and self.use_grayscale:
            use_setting = "grayscale_bb"
        elif self.use_white_bg and self.use_grayscale:
            use_setting = "grayscale_wb"

        self.bg_ccode = self.bg_ccodes[use_setting]
        self.fg_ccode = self.fg_ccodes[use_setting]
        self.empty_bin_ccode = self.empty_bin_ccodes[use_setting]
        self.fill_bin_ccode = self.fill_bin_ccodes[use_setting]
        self.max_bin_ccode = self.max_bin_ccodes[use_setting]
        self.graph_ccode = self.graph_ccodes[use_setting]
        self.bar_ccodes = self.bar_ccodes_lists[use_setting]

        self.ccodes = self.cmaps[use_setting]

        n_colors_current = len(self.ccodes)
        new_ccodes = []

        if self.use_n_colors < n_colors_current:
            for i in np.round(np.linspace(0, n_colors_current - 1, self.use_n_colors)).astype(int):
                new_ccodes.append(self.ccodes[i])
        else:
            new_ccodes = [self.ccodes[i%n_colors_current] for i in range(self.use_n_colors)]

        self.ccodes = new_ccodes
        self.use_n_colors = len(self.ccodes)

