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

ccodes = cmaps[0]



def get_color_code(z_val, z_norm, color_z_lims):

    if z_norm == 1.0:
        return ccodes[-1]
    elif z_norm == 0.0:
        return ccodes[0]

    i = 0
    for j, lim in enumerate(color_z_lims):
        if z_val >= lim:
            i = j
        else:
            break
    return ccodes[i]


def get_marker(z_norm):

    return regular_marker


#
# Run
#

def run(args):

    assert args.cmap_index in range(len(cmaps))

    global ccodes 
    global bg_ccode
    global fg_ccode
    global empty_bin_ccode
    global empty_bin_marker
    global special_marker

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index
    z_index = args.z_index

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range
    z_range = args.z_range

    read_slice = slice(*args.read_slice)

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
        # ccodes = ccodes_color_wb

    if args.use_grayscale:
        if use_white_bg:
            ccodes = cmaps_grayscale[1]
            empty_bin_ccode = defaults.empty_bin_ccode_grayscale_wb
        else:
            ccodes = cmaps_grayscale[0]
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
    # Read datasets from file
    #

    dsets, dset_names = utils.read_input_file(input_file, 
                                              [x_index, y_index, z_index], 
                                              read_slice, 
                                              delimiter=args.delimiter)
    x_data, y_data, z_data = dsets
    x_name, y_name, z_name = dset_names

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(z_data)

    filter_datasets, filter_names = utils.get_filters(input_file, 
                                                      filter_indices, 
                                                      read_slice=read_slice, 
                                                      delimiter=args.delimiter)

    if use_filters:
        x_data, y_data, z_data = utils.apply_filters([x_data, y_data, z_data], 
                                                     filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    z_transf_expr = args.z_transf_expr
    x = x_data
    y = y_data
    z = z_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if z_transf_expr != "":
        z_data = eval(z_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]
    if not z_range:
        z_range = [np.min(z_data), np.max(z_data)]

    # Get z max and minimum
    z_min, z_max = z_range

    # z_norm = (z_data - z_min) / (z_max - z_min)

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
                z_norm = 0.0
                if (z_max != z_min):
                    z_norm = (z_val - z_min) / (z_max - z_min)

                ccode = get_color_code(z_val, z_norm, color_z_lims)
                marker = get_marker(z_norm)

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

    x_label = x_name
    y_label = y_name
    z_label = z_name + " [binned average]"


    #
    # Add info text
    #

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, fg_ccode, bg_ccode, ff2, x_label, x_range,
        x_bin_width=dx, y_label=y_label, y_range=y_range, y_bin_width=dy,
        z_label=z_label, z_range=z_range, 
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        z_transf_expr=z_transf_expr,
        filter_names=filter_names, mode_name="average")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
