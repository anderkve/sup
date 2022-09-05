# -*- coding: utf-8 -*-
import numpy as np
import sup.defaults as defaults
import sup.utils as utils
from collections import OrderedDict
from sup.colors import cmaps, cmaps_grayscale
from sup.ccodesettings import CCodeSettings


#
# Variables for colors, markers, padding, etc
#

regular_marker = defaults.regular_marker
special_marker = defaults.special_marker

empty_bin_marker = defaults.empty_bin_marker_2d


def get_color_code(ccs, z_val, z_norm, color_z_lims):

    if z_norm == 1.0:
        return ccs.ccodes[-1]
    elif z_norm == 0.0:
        return ccs.ccodes[0]

    i = 0
    for j, lim in enumerate(color_z_lims):
        if z_val >= lim:
            i = j
        else:
            break
    return ccs.ccodes[i]


def get_marker(z_norm):

    return regular_marker


#
# Run
#

def run(args):

    global empty_bin_marker
    global special_marker

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index

    w_index = args.w_index
    use_weights = bool(w_index is not None)

    normalize_histogram = args.normalize_histogram

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    z_range_user = args.z_range
    user_defined_z_range = bool(z_range_user is not None)

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    ccs = CCodeSettings()
    ccs.ccodes = ccs.cmaps[args.cmap_index]
    ccs.switch_settings(use_white_bg=args.use_white_bg, 
                        use_grayscale=args.use_grayscale)
    ccs.set_n_colors(args.n_colors)

    if args.reverse_colormap:
        ccs.ccodes = ccs.ccodes[::-1]

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    x_name = None
    x_data = None
    y_name = None
    y_data = None
    w_name = None
    w_data = None

    if use_weights:
        dsets, dset_names = utils.read_input_file(input_file,
                                                  [x_index, y_index, w_index],
                                                  read_slice,
                                                  delimiter=args.delimiter)
        x_data, y_data, w_data = dsets
        x_name, y_name, w_name = dset_names
        utils.check_weights(w_data, w_name)
    else:
        dsets, dset_names = utils.read_input_file(input_file,
                                                  [x_index, y_index],
                                                  read_slice,
                                                  delimiter=args.delimiter)
        x_data, y_data = dsets
        x_name, y_name = dset_names
        w_data = np.ones(len(x_data))

    filter_datasets, filter_names = utils.get_filters(input_file,
                                                      filter_indices,
                                                      read_slice=read_slice,
                                                      delimiter=args.delimiter)

    if use_filters:
        x_data, y_data, w_data = utils.apply_filters([x_data, y_data, w_data],
                                                     filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    w_transf_expr = args.w_transf_expr
    z_transf_expr = args.z_transf_expr
    # @todo: add the x,y,w variables to a dictionary of allowed arguments
    #        to eval()
    x = x_data
    y = y_data
    w = w_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if w_transf_expr != "":
        w_data = eval(w_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]



    #
    # Get a dict with info per bin
    #

    bins_content_unweighted,_ ,_  = np.histogram2d(
        x_data, y_data, bins=xy_bins, range=[x_range, y_range], 
        density=normalize_histogram)
    bins_content, x_bin_limits, y_bin_limits = np.histogram2d(
        x_data, y_data, bins=xy_bins, range=[x_range, y_range], weights=w_data, 
        density=normalize_histogram)

    # Apply z-axis transformation
    z = bins_content
    if z_transf_expr != "":
        bins_content = eval(z_transf_expr)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    bins_info = OrderedDict()
    for i,xi in enumerate(x_bin_centres):
        for j,yj in enumerate(y_bin_centres):

            bin_key = (i,j)
            z_val = bins_content[bin_key]      
            bin_count = bins_content_unweighted[bin_key]

            if bin_count > 0:
                bins_info[bin_key] = (xi, yj, z_val)

    # Get z max and minimum from data if not set by the user
    z_range = None
    if user_defined_z_range:
        z_range = z_range_user
    else:
        z_range = [
            np.min(bins_content[bins_content > -np.inf]), np.max(bins_content)
        ]
    z_min, z_max = z_range 

    # Set color limits
    color_z_lims = list(np.linspace(z_min, z_max, len(ccs.ccodes)+1))


    #
    # Generate string to be printed
    #

    plot_lines = []
    fig_width = 0
    for yi in range(xy_bins[1]):

        yi_line = utils.prettify(" ", ccs.fg_ccode, ccs.bg_ccode)

        for xi in range(xy_bins[0]):

            xiyi = (xi,yi)

            ccode = ccs.empty_bin_ccode
            marker = empty_bin_marker

            if xiyi in bins_info.keys():
                z_val = bins_info[xiyi][2]
                z_norm = 0.0
                if (z_max != z_min):
                    z_norm = (z_val - z_min) / (z_max - z_min)
                if z_norm > 1.0:
                    z_norm = 1.0
                elif z_norm < 0.0:
                    z_norm = 0.0

                ccode = get_color_code(ccs, z_val, z_norm, color_z_lims)
                marker = get_marker(z_norm)

            # Add point to line
            yi_line += utils.prettify(marker, ccode, ccs.bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 5 + len(ff.format(0))
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, ccs.fg_ccode,
                                                      ccs.bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits,
                                mod_func=axes_mod_func, floatf=ff)

    # Add blank top line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode,
                                              insert_pos=0)


    #
    # Add colorbar, legend, etc
    #

    plot_lines, fig_width = utils.generate_colorbar(plot_lines, fig_width, ff,
                                                    ccs, color_z_lims)
    

    # max bin legend
    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(
        input_str, input_fg_ccode, ccs.bg_ccode, bold=True)

    maxbin_content = -np.inf
    maxbin_x_index = 0
    maxbin_y_index = 0
    for bin_key, bin_tuple in bins_info.items():
        z_val = bin_tuple[2]
        if z_val > maxbin_content:
            maxbin_content = z_val
            maxbin_x_index, maxbin_y_index = bin_key

    maxbin_xlimits = [
        x_bin_limits[maxbin_x_index], x_bin_limits[maxbin_x_index+1]
    ]
    maxbin_ylimits = [
        y_bin_limits[maxbin_y_index], y_bin_limits[maxbin_y_index+1]
    ]

    maxbin_str = "max bin:  x: "
    maxbin_str += ("(" + ff2 + ", " + ff2 + ")").format(maxbin_xlimits[0], 
                                                        maxbin_xlimits[1])
    maxbin_str += "  y: "
    maxbin_str += ("(" + ff2 + ", " + ff2 + ")").format(maxbin_ylimits[0], 
                                                        maxbin_ylimits[1])
    maxbin_str += "  bin height: "
    maxbin_str += (ff2).format(maxbin_content)

    legend_maxbin_entries = []
    legend_maxbin_entries.append(("", ccs.fg_ccode, maxbin_str, ccs.fg_ccode))
    legend_maxbin, legend_maxbin_width = utils.generate_legend(
        legend_maxbin_entries, legend_mod_func, sep="  ", internal_sep=" ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend_maxbin, 
                                              legend_maxbin_width, plot_lines, 
                                              fig_width, ccs.fg_ccode, 
                                              ccs.bg_ccode)


    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


    #
    # Set labels
    #

    x_label = x_name
    y_label = y_name
    z_label = "bin height"
    w_label = w_name

    #
    # Add info text
    #

    plot_lines, fig_width = utils. add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff2, x_label, x_range,
        x_bin_width=dx, y_label=y_label, y_range=y_range, y_bin_width=dy,
        z_label=z_label, z_range=z_range, 
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        z_transf_expr=z_transf_expr, z_normalized_hist=normalize_histogram,
        w_label=w_label, w_transf_expr=w_transf_expr, 
        filter_names=filter_names, mode_name="histogram")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
