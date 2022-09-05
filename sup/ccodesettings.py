# -*- coding: utf-8 -*-
import numpy as np
import sup.defaults as defaults

class CCodeSettings:

    def __init__(self):
        self.bg_ccode_bb = defaults.bg_ccode_bb
        self.bg_ccode_wb = defaults.bg_ccode_wb
        self.fg_ccode_bb = defaults.fg_ccode_bb
        self.fg_ccode_wb = defaults.fg_ccode_wb

        self.empty_bin_ccode_color_bb = defaults.empty_bin_ccode_color_bb
        self.empty_bin_ccode_color_wb = defaults.empty_bin_ccode_color_wb
        self.empty_bin_ccode_grayscale_bb = defaults.empty_bin_ccode_grayscale_bb
        self.empty_bin_ccode_grayscale_wb = defaults.empty_bin_ccode_grayscale_wb

        self.fill_bin_ccode_color_bb = defaults.fill_bin_ccode_color_bb
        self.fill_bin_ccode_color_wb = defaults.fill_bin_ccode_color_wb
        self.fill_bin_ccode_grayscale_bb = defaults.fill_bin_ccode_grayscale_bb
        self.fill_bin_ccode_grayscale_wb = defaults.fill_bin_ccode_grayscale_wb

        self.max_bin_ccode_color_bb = defaults.max_bin_ccode_color_bb
        self.max_bin_ccode_color_wb = defaults.max_bin_ccode_color_wb
        self.max_bin_ccode_grayscale_bb = defaults.max_bin_ccode_grayscale_bb
        self.max_bin_ccode_grayscale_wb = defaults.max_bin_ccode_grayscale_wb

        self.graph_ccode_color_bb = defaults.graph_ccode_color_bb
        self.graph_ccode_color_wb = defaults.graph_ccode_color_wb
        self.graph_ccode_grayscale_bb = defaults.graph_ccode_grayscale_bb
        self.graph_ccode_grayscale_wb = defaults.graph_ccode_grayscale_wb

        self.bar_ccodes_color = defaults.bar_ccodes_color
        self.bar_ccodes_grayscale = defaults.bar_ccodes_grayscale

        self.cmap_grayscale_bb = [233, 236, 239, 242, 244, 247, 250, 253, 255, 231]
        self.cmap_grayscale_wb = [232, 235, 238, 240, 243, 246, 248, 251, 253, 255][::-1]

        self.cmaps = [
            [53, 56, 62, 26, 31, 36, 42, 47, 154, 226],         # viridis
            [18, 20, 27, 45, 122, 155, 226, 214, 202, 196],     # jet
            [233, 234, 53, 126, 162, 199, 202, 208, 220, 226],  # inferno
            [25, 32, 81, 123, 195, 230, 222, 214, 202, 1],      # blue-red
        ]

        self.cmap_color_bb = self.cmaps[0]
        self.cmap_color_wb = self.cmaps[0]


        # Active settings
        self.bg_ccode = self.bg_ccode_bb
        self.fg_ccode = self.fg_ccode_bb
        self.empty_bin_ccode = self.empty_bin_ccode_color_bb
        self.fill_bin_ccode = self.fill_bin_ccode_color_bb
        self.max_bin_ccode = self.max_bin_ccode_color_bb
        self.graph_ccode = self.graph_ccode_color_bb
        self.bar_ccodes = self.bar_ccodes_color
        self.ccodes = self.cmap_color_bb


    def switch_settings(self, use_white_bg=False, use_grayscale=False):
        if use_white_bg and use_grayscale:
            self.bg_ccode = self.bg_ccode_wb
            self.fg_ccode = self.fg_ccode_wb
            self.empty_bin_ccode = self.empty_bin_ccode_grayscale_wb
            self.fill_bin_ccode = self.fill_bin_ccode_grayscale_wb
            self.max_bin_ccode = self.max_bin_ccode_grayscale_wb
            self.graph_ccode = self.graph_ccode_grayscale_wb
            self.bar_ccodes = self.bar_ccodes_grayscale
            self.ccodes = self.cmap_grayscale_wb

        elif use_white_bg and not use_grayscale:
            self.bg_ccode = self.bg_ccode_wb
            self.fg_ccode = self.fg_ccode_wb
            self.empty_bin_ccode = self.empty_bin_ccode_color_wb
            self.fill_bin_ccode = self.fill_bin_ccode_color_wb
            self.max_bin_ccode = self.max_bin_ccode_color_wb
            self.graph_ccode = self.graph_ccode_color_wb
            self.bar_ccodes = self.bar_ccodes_color
            self.ccodes = self.cmap_color_wb

        elif not use_white_bg and use_grayscale:        
            self.bg_ccode = self.bg_ccode_bb
            self.fg_ccode = self.fg_ccode_bb
            self.empty_bin_ccode = self.empty_bin_ccode_grayscale_bb
            self.fill_bin_ccode = self.fill_bin_ccode_grayscale_bb
            self.max_bin_ccode = self.max_bin_ccode_grayscale_bb
            self.graph_ccode = self.graph_ccode_grayscale_bb
            self.bar_ccodes = self.bar_ccodes_grayscale
            self.ccodes = self.cmap_grayscale_bb

        elif not use_white_bg and not use_grayscale:
            self.bg_ccode = self.bg_ccode_bb
            self.fg_ccode = self.fg_ccode_bb
            self.empty_bin_ccode = self.empty_bin_ccode_color_bb
            self.fill_bin_ccode = self.fill_bin_ccode_color_bb
            self.max_bin_ccode = self.max_bin_ccode_color_bb
            self.graph_ccode = self.graph_ccode_color_bb
            self.bar_ccodes = self.bar_ccodes_color
            self.ccodes = self.cmap_color_bb


    def set_n_colors(self, n_colors):
        n_colors_current = len(self.ccodes)
        new_ccodes = []
        for i in np.round(np.linspace(0, n_colors_current - 1, n_colors)).astype(int):
            new_ccodes.append(self.ccodes[i])
        self.ccodes = new_ccodes

