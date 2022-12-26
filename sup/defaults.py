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

    fg_ccode_bb (int): The default foreground color code for black background.

    bg_ccode_wb (int): The default background color code for white background.

    fg_ccode_wb (int): The default foreground color code for white background.

    regular_marker (string): The default marker used to fill plots.

    regular_marker_up (string): The default marker, shifted upwards.

    regular_marker_down (string): The default marker, shifted downwards.

    fill_marker (string): The default marker used to fill vertical blocks,
        e.g. for use in 1d histograms.

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

    fill_bin_ccode_color_bb (int): The default color code for "fill bins", 
        in plots with black background.

    fill_bin_ccode_color_wb (int): The default color code for "fill bins",
        in plots with white background.

    fill_bin_ccode_grayscale_bb (int): The default color code for "fill bins"
        in grayscale plots with black background.

    fill_bin_ccode_grayscale_wb (int): The default color code for "fill bins"
        in grayscale plots with white background.

    max_bin_ccode_color_bb (int): The default color code for the bin/marker
        with the max z value, in plots with black background.

    max_bin_ccode_color_wb (int): The default color code for the bin/marker
        with the max z value, in plots with white background.

    max_bin_ccode_grayscale_bb (int): The default color code for the bin/marker
        with the max z value, in grayscale plots with black background.

    max_bin_ccode_grayscale_wb (int): The default color code for the bin/marker
        with the max z value, in grayscale plots with white background.

    graph_ccode_color_bb (int): The default color code for 1d graph drawing,
        in plots with black background.

    graph_ccode_color_wb (int): The default color code for 1d graph drawing,
        in plots with white background.

    graph_ccode_grayscale_bb (int): The default color code for 1d graph drawing,
        in grayscale plots with black background.

    graph_ccode_grayscale_wb (int): The default color code for 1d graph drawing,
        in grayscale plots with white background.

    bar_ccodes_color (list of ints): The default color codes for drawing
        horizontal bars (e.g. CR/CI bars) below plots.

    bar_ccodes_grayscale (list of ints): The default color codes for drawing
        horizontal bars (e.g. CR/CI bars) below grayscale plots.

    cmap_color_bb (list of ints): The default color map for plots with black
        background.

    cmap_color_wb (list of ints): The default color map for plots with white
        background.

    cmap_grayscale_bb (list of ints): The default color map for grayscale plots
        with black background.

    cmap_grayscale_wb (list of ints): The default color map for grayscale plots
        with white background.

    n_decimals (int): The default numer of decimals.

"""

import sup.colors as colors


left_padding = 2*" "

xy_bins = (40, 40)

bg_ccode_bb, fg_ccode_bb = 16, 231
bg_ccode_wb, fg_ccode_wb = 231, 16

regular_marker = " ■"
regular_marker_up = " ▀"
regular_marker_down = " ▄"

fill_marker = " █"

special_marker = " 🟊"

empty_bin_marker_1d = "  "
empty_bin_marker_2d = " □"

empty_bin_ccode_color_bb = 237
empty_bin_ccode_color_wb = 252

empty_bin_ccode_grayscale_bb = 237
empty_bin_ccode_grayscale_wb = 252

fill_bin_ccode_color_bb = 237
fill_bin_ccode_color_wb = 252

fill_bin_ccode_grayscale_bb = 237
fill_bin_ccode_grayscale_wb = 252

max_bin_ccode_color_bb = 231
max_bin_ccode_color_wb = 232

max_bin_ccode_grayscale_bb = 231
max_bin_ccode_grayscale_wb = 232

graph_ccode_color_bb = 237
graph_ccode_color_wb = 252

graph_ccode_grayscale_bb = 237
graph_ccode_grayscale_wb = 252

bar_ccodes_color = [4,12]
bar_ccodes_grayscale = [243, 240]

cmap_color_bb = colors.cmaps[0]
cmap_color_wb = colors.cmaps[0]
cmap_grayscale_bb = colors.cmaps_grayscale[0]
cmap_grayscale_wb = colors.cmaps_grayscale[1]

n_decimals = 2

