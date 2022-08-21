# -*- coding: utf-8 -*-

"""Default settings.

A sup module for collecting default settings that are used by several run modes. 

Attributes:
    left_padding (string): The default amount of whitespace on the left side 
        of the plots.

    xy_bins (pair of ints): The default number of bins to be used along the 
        x-axis and y-axis.

    ff (format string): The default format string for floating-point numbers,
        with a reserved space for the sign.

    ff2 (format string): The default format string for floating-point numbers,
        without a reserverd space for the sign.

    bg_ccode_bb (int): The default background color code for black background.

    fg_ccode_bb (int): The default forground color code for black background.

    bg_ccode_wb (int): The default background color code for white background.

    fg_ccode_wb (int): The default forground color code for white background.

    regular_marker (string): The default marker used to fill plots.

    special_marker (string): The default marker used to highlight special points
        in the plots.

    empty_bin_marker_1d (string): The default marker for empty bins in 1d plots.

    empty_bin_marker_2d (string): The default marker for empty bins in 2d plots.

    empty_bin_ccode_color_bb (int): The default color code for empty bins
        in plots with black background.

    empty_bin_ccode_color_wb (int): The default color code for empty bins
        in plots with white background.

    empty_bin_ccode_grayscale_bb (int): The default color code for empty bins
        in grayscale plots with black background.

    empty_bin_ccode_grayscale_wb (int): The default color code for empty bins
        in grayscale plots with white background.

    n_decimals (int): The default numer of decimals.

"""

left_padding = 2*" "

xy_bins = (40, 40)

bg_ccode_bb, fg_ccode_bb = 16, 231
bg_ccode_wb, fg_ccode_wb = 231, 16

regular_marker = " ■"
special_marker = " 🟊"

empty_bin_marker_1d = "  "
empty_bin_marker_2d = " □"

empty_bin_ccode_color_bb = 237
empty_bin_ccode_color_wb = 252

empty_bin_ccode_grayscale_bb = 237
empty_bin_ccode_grayscale_wb = 252

n_decimals = 2

