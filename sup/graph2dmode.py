# -*- coding: utf-8 -*-
import numpy as np
import sup.defaults as defaults
import sup.utils as utils
from sup.colors import cmaps, cmaps_grayscale


#
# Variables for colors, markers, padding, etc
#

bg_ccode = defaults.bg_ccode_bb
fg_ccode = defaults.fg_ccode_bb

regular_marker = defaults.regular_marker
special_marker = defaults.special_marker

empty_bin_marker = defaults.empty_bin_marker_2d

empty_bin_ccode = defaults.empty_bin_ccode_color_bb

max_bin_ccode_grayscale_bb = 231
max_bin_ccode_grayscale_wb = 232
max_bin_ccode_grayscale = max_bin_ccode_grayscale_bb

max_bin_ccode_color_bb = 231
max_bin_ccode_color_wb = 232
max_bin_ccode = max_bin_ccode_color_bb

ccodes = cmaps[0]



def get_color_code(z_val, color_z_lims):

    if z_val >= color_z_lims[-1]:
        return ccodes[-1]
    elif z_val <= color_z_lims[0]:
        return ccodes[0]        
    else:
        i = 0
        for j, lim in enumerate(color_z_lims):
            if z_val > lim:
                i = j
            else:
                break
        return ccodes[i]
    raise Exception("Unexpected z_val. This shouldn't happen...")


def get_marker():

    return regular_marker



#
# Run
#

def run(args):

    assert args.cmap_index in range(len(cmaps))

    global ccodes 
    global bg_ccode
    global fg_ccode
    global max_bin_ccode
    global max_bin_ccode_grayscale
    global empty_bin_ccode
    global empty_bin_marker
    global special_marker

    function_str = args.function

    x_range = args.x_range
    y_range = args.y_range
    z_range = args.z_range

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    cmap_index = args.cmap_index
    ccodes = cmaps[cmap_index]
    use_white_bg = args.use_white_bg
    if use_white_bg:
        bg_ccode = defaults.bg_ccode_wb
        fg_ccode = defaults.fg_ccode_wb
        empty_bin_ccode = defaults.empty_bin_ccode_color_wb
        max_bin_ccode = max_bin_ccode_color_wb
        # ccodes = ccodes_color_wb

    if args.use_grayscale:
        if use_white_bg:
            ccodes = cmaps_grayscale[1]
            max_bin_ccode = max_bin_ccode_grayscale_wb
            empty_bin_ccode = defaults.empty_bin_ccode_grayscale_wb
        else:
            ccodes = cmaps_grayscale[0]
            max_bin_ccode = max_bin_ccode_grayscale_bb
            empty_bin_ccode = defaults.empty_bin_ccode_grayscale_bb

    n_colors = args.n_colors
    if n_colors < 1:
        n_colors = 1
    elif n_colors > 10:
        n_colors = 10
    ccodes = [
        ccodes[int(i)] for i in np.round(np.linspace(0,len(ccodes)-1,n_colors))
    ]

    if args.reverse_colormap:
        ccodes = ccodes[::-1]

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Generate datasets from function defintion
    #

    # Generate x dataset based on x range and number of bins
    if not x_range:
        x_range = [0.0, 1.0]
    if not y_range:
        y_range = [0.0, 1.0]

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range
    y_min, y_max = y_range

    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)
    y_bin_limits = np.linspace(y_min, y_max, y_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    x_data = []
    y_data = []
    z_data = []
    for x in x_bin_centres:
        for y in y_bin_centres:
            x_data.append(x)
            y_data.append(y)
            z_data.append(eval(function_str))

    x_data = np.array(x_data)
    y_data = np.array(y_data)
    z_data = np.array(z_data)

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(z_data)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]
    if not z_range:
        z_range = [np.min(z_data), np.max(z_data)]

    z_min, z_max = z_range

    # Set color limits
    color_z_lims = list(np.linspace(z_min, z_max, len(ccodes)+1))

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg(
        x_data, y_data, z_data, xy_bins, x_range, y_range)


    #
    # Generate string to be printed
    #

    plot_lines = []
    fig_width = 0
    for yi in range(xy_bins[1]):

        yi_line = utils.prettify(" ", fg_ccode, bg_ccode)

        for xi in range(xy_bins[0]):

            xiyi = (xi,yi)

            ccode = empty_bin_ccode
            marker = empty_bin_marker

            if xiyi in bins_info.keys():
                z_val = bins_info[xiyi][2]
                # z_norm = 0.0
                # if (z_max != z_min):
                #     z_norm = (z_val - z_min) / (z_max - z_min)

                ccode = get_color_code(z_val, color_z_lims)
                marker = get_marker()

            # Add point to line
            yi_line += utils.prettify(marker, ccode, bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 5 + len(ff.format(0))
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, fg_ccode, 
                                                      bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits, 
                                mod_func=axes_mod_func, floatf=ff)

    # Add blank top line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              fg_ccode, bg_ccode, insert_pos=0)


    #
    # Add colorbar, legend, etc
    #

    plot_lines, fig_width = utils.generate_colorbar(plot_lines, fig_width, ff,
                                                    ccodes, color_z_lims, 
                                                    fg_ccode, bg_ccode, 
                                                    empty_bin_ccode)

        
    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, fg_ccode, bg_ccode)


    #
    # Set labels
    #

    x_label = "x"
    y_label = "y"
    z_label = "f(x,y) = " + function_str


    #
    # Add info text
    #

    info_lines = utils.generate_info_text(ff2, 
                                          x_label, x_range, 
                                          y_label=y_label, y_range=y_range, 
                                          z_label=z_label, z_range=z_range, 
                                          mode_name="graph")

    for i,line in enumerate(info_lines):
        pretty_line = utils.prettify(line + "  ", fg_ccode, bg_ccode, 
                                     bold=False)
        plot_lines, fig_width = utils.insert_line(pretty_line, len(line), 
                                                  plot_lines, fig_width,
                                                  fg_ccode, bg_ccode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
