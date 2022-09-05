# -*- coding: utf-8 -*-
import numpy as np
import sup.defaults as defaults
import sup.utils as utils
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def get_color_code(ccs, z_val):

    if z_val in [1,2]:
        return ccs.graph_ccode
    elif z_val == 0:
        return ccs.empty_bin_ccode
    else:
        raise Exception("Unexpected z_val. This shouldn't happen...")


def get_marker(ms, z_val):

    if z_val == 2:
        return ms.regular_marker_up
    elif z_val == 1:
        return ms.regular_marker_down
    elif z_val == 0:
        return ms.empty_bin_marker
    else:
        raise Exception("Unexpected z_val. This shouldn't happen...")


#
# Run
#

def run(args):

    function_str = args.function

    x_range = args.x_range
    y_range = args.y_range

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    ccs = CCodeSettings()
    ccs.graph_ccodes["grayscale_bb"] = 231
    ccs.graph_ccodes["grayscale_wb"] = 232
    ccs.graph_ccodes["color_bb"] = 4
    ccs.graph_ccodes["color_wb"] = 12
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.update()

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_1d

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Generate datasets from function defintion
    #

    # Generate x dataset based on x range and number of bins
    if not x_range:
        x_range = [0.0, 1.0]

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range

    # Get index of max-z point in each bin
    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx

    x_data = x_bin_centres

    y_data = np.zeros(shape=x_data.shape)

    # Need this declaration such the 'x' can be used in the eval input string
    x = x_data

    # Create y data set by evaluating the function_str
    y_data = eval(function_str)

    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]


    #
    # Get a dict with info per bin
    #

    # @todo Don't use the 'avg' version for this.
    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg_1d(
        x_data, y_data, xy_bins, x_range, y_range, split_marker=True)


    #
    # Generate string to be printed
    #

    plot_lines = []
    fig_width = 0
    for yi in range(xy_bins[1]):

        yi_line = utils.prettify(" ", ccs.fg_ccode, ccs.bg_ccode)

        for xi in range(xy_bins[0]):

            xiyi = (xi,yi)

            cc = ccs.empty_bin_ccode
            marker = ms.empty_bin_marker

            if xiyi in bins_info.keys():
                z_val = bins_info[xiyi][2]

                cc = get_color_code(ccs, z_val)
                marker = get_marker(ms, z_val)

            # Add point to line
            yi_line += utils.prettify(marker, cc, ccs.bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 5 + len(ff.format(0))
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, ccs.fg_ccode, 
                                                      ccs.bg_ccode, bold=True)
    fill_mod_func = lambda input_str : utils.prettify(input_str, 
                                                      ccs.empty_bin_ccode,
                                                      ccs.bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits,
                                mod_func=axes_mod_func, 
                                mod_func_2=fill_mod_func, floatf=ff,
                                add_y_grid_lines=True)

    # Add blank top line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, 
                                              ccs.fg_ccode, ccs.bg_ccode,
                                              insert_pos=0)


    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


    #
    # Set labels
    #

    x_label = "x"
    y_label = "f(x) = " + function_str


    #
    # Add info text
    #

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff2, 
        x_label, x_range, y_label=y_label, y_range=y_range, mode_name="graph")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
