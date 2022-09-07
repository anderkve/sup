# -*- coding: utf-8 -*-

"""sup.avg2dmode

A sup run mode that produces a 2d map of the average z value for each bin 
in the (x,y) plane.

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
import sup.colors as colors
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'avg2d' run mode.

    This function 
    - interprets the command-line arguments for this run mode;
    - reads and processes the data as appropriate for this run mode;
    - constructs the full output as a list of strings; and
    - prints the output to screen.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    
    """

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
    
    ccs = CCodeSettings()
    ccs.cmaps["color_bb"] = colors.cmaps[args.cmap_index]
    ccs.cmaps["color_wb"] = colors.cmaps[args.cmap_index]
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.use_n_colors = args.n_colors
    ccs.update()

    if args.reverse_colormap:
        ccs.ccodes = ccs.ccodes[::-1]

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_2d

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

    # Set color limits
    color_z_lims = list(np.linspace(z_min, z_max, len(ccs.ccodes)+1))

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg(
        x_data, y_data, z_data, xy_bins, x_range, y_range)


    #
    # Generate string to be printed
    #

    # Define a function that returns the color code and marker for any bin 
    # coordinate xiyi in the plot
    def get_ccode_and_marker(xiyi):

        z_val = bins_info[xiyi][2]
        z_norm = 0.0
        if (z_max != z_min):
            z_norm = (z_val - z_min) / (z_max - z_min)

        # Set color code
        ccode = None
        if z_norm == 1.0:
            ccode = ccs.ccodes[-1]
        elif z_norm == 0.0:
            ccode = ccs.ccodes[0]
        else:
            i = 0
            for j, lim in enumerate(color_z_lims):
                if z_val >= lim:
                    i = j
                else:
                    break
            ccode = ccs.ccodes[i]

        # Set marker
        marker = ms.regular_marker

        return ccode, marker


    # Pass the above function to utils.fill_plot, receive back the generated
    # plot as a list of strings
    plot_lines, plot_width = utils.fill_plot(xy_bins, bins_info, ccs, ms, 
                                             get_ccode_and_marker)

    # Total figure width
    fig_width = utils.figure_width_from_plot_width(plot_width, ff)

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


    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


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
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff2, x_label, 
        x_range, x_bin_width=dx, y_label=y_label, y_range=y_range, 
        y_bin_width=dy, z_label=z_label, z_range=z_range, 
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        z_transf_expr=z_transf_expr,
        filter_names=filter_names, mode_name="average")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
