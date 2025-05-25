# -*- coding: utf-8 -*-

"""sup.avg1dmode

A sup run mode that produces a 1d graph of the average y value for each bin 
along the x axis.

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'avg1d' run mode.

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

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins

    ccs = CCodeSettings()
    ccs.graph_ccodes["grayscale_bb"] = 231
    ccs.graph_ccodes["grayscale_wb"] = 232
    ccs.graph_ccodes["color_bb"] = 5
    ccs.graph_ccodes["color_wb"] = 6
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.update()

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_1d

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    dsets, dset_names = utils.read_input_file(args.input_file, 
                                              [x_index, y_index],
                                              read_slice, 
                                              delimiter=args.delimiter,
                                              stdin_format=args.stdin_format)
    x_data, y_data = dsets
    x_name, y_name = dset_names

    filter_datasets, filter_names = utils.get_filters(args.input_file, 
                                                      filter_indices, 
                                                      read_slice=read_slice, 
                                                      delimiter=args.delimiter,
                                                      stdin_format=args.stdin_format)

    if use_filters:
        x_data, y_data = utils.apply_filters([x_data, y_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr

    # Need this declaration such the 'x' can be used in the eval input string
    x = x_data
    y = y_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]


    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg_1d(
        x_data, y_data, xy_bins, x_range, y_range, split_marker=True)


    #
    # Generate string to be printed
    #

    # Define a function that returns the color code and marker for any bin 
    # coordinate xiyi in the plot
    def get_ccode_and_marker(xiyi):
        """Determines the color code and plot marker for a given bin.

        The determination is based on the bin's z-value, which indicates
        whether the bin is empty or if its corresponding data point is
        above or below the average y value for its x-bin.

        This function relies on `bins_info`, `ccs` (CCodeSettings), and
        `ms` (MarkerSettings) from the outer scope.

        Args:
            xiyi (tuple): The (x_bin_index, y_bin_index) coordinates
                of the bin.

        Returns:
            tuple: A tuple `(ccode, marker)` containing the color code (int)
                and marker string for the bin.
        """

        z_val = bins_info[xiyi][2]

        # Set color code
        ccode = None
        if z_val in [1,2]:
            ccode = ccs.graph_ccode
        elif z_val == 0:
            ccode = ccs.empty_bin_ccode
        else:
            raise Exception("Unexpected z_val. This shouldn't happen...")

        # Set marker
        marker = None
        if z_val == 2:
            marker = ms.regular_marker_up
        elif z_val == 1:
            marker = ms.regular_marker_down
        elif z_val == 0:
            marker = ms.empty_bin_marker
        else:
            raise Exception("Unexpected z_val. This shouldn't happen...")

        return ccode, marker


    # Pass the above function to utils.fill_plot, receive back the generated
    # plot (including axes) as a list of strings.
    plot_lines, fig_width = utils.fill_plot(xy_bins, bins_info, x_bin_limits,
                                            y_bin_limits, ccs, ms, 
                                            get_ccode_and_marker, ff,
                                            add_y_grid_lines=True)


    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


    #
    # Set labels
    #

    x_label = x_name
    y_label = y_name


    #
    # Add info text
    #

    dx = x_bin_limits[1] - x_bin_limits[0]

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff=ff2, 
        x_label=x_label, x_range=x_range, x_bin_width=dx,
        y_label=y_label, y_range=y_range, 
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        filter_names=filter_names, mode_name="average")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
