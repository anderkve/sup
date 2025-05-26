# -*- coding: utf-8 -*-

"""sup.maxmin2dmode

A sup run mode that produces a 2d map of the maximum or minimum z value for 
each bin in the (x,y) plane.

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
import sup.colors as colors
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run_max(args):
    """Calls the main 'run' function to plot maximum z-values per (x,y)-bin.

    This is a wrapper function that calls the main `run` function of
    `maxmin2dmode` with the mode explicitly set to "max". It's used to
    generate a 2D map of the maximum z-value for each (x,y)-bin.

    Args:
        args (argparse.Namespace): The parsed command-line arguments,
            which are passed through to the main `run` function.

    Returns:
        None
    """
    run(args, "max")

def run_min(args):
    """Calls the main 'run' function to plot minimum z-values per (x,y)-bin.

    This is a wrapper function that calls the main `run` function of
    `maxmin2dmode` with the mode explicitly set to "min". It's used to
    generate a 2D map of the minimum z-value for each (x,y)-bin.

    Args:
        args (argparse.Namespace): The parsed command-line arguments,
            which are passed through to the main `run` function.

    Returns:
        None
    """
    run(args, "min")

def run(args, mode):
    """The main function for the 'maxmin2d' run mode.

    This function 
    - interprets the command-line arguments for this run mode;
    - reads and processes the data as appropriate for this run mode;
    - constructs the full output as a list of strings; and
    - prints the output to screen.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

        mode (string): The specific run mode, "max" or "min".
    
    """

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index
    z_index = args.z_index

    s_index = args.z_index
    if args.s_index is not None:
        s_index = args.s_index
    s_type = mode

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

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_2d

    if args.reverse_colormap:
        ccs.ccodes = ccs.ccodes[::-1]

    highlight_maxmin_point = not(args.no_star)

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    dsets, dset_names = utils.read_input_file(args.input_file, 
                                              [x_index,y_index,z_index,s_index],
                                              read_slice, 
                                              delimiter=args.delimiter,
                                              stdin_format=args.stdin_format)
    x_data, y_data, z_data, s_data = dsets
    x_name, y_name, z_name, s_name = dset_names

    filter_datasets, filter_names = utils.get_filters(args.input_file, 
                                                      filter_indices, 
                                                      read_slice=read_slice,
                                                      delimiter=args.delimiter,
                                                      stdin_format=args.stdin_format)

    if use_filters:
        x_data, y_data, z_data, s_data = utils.apply_filters(
                [x_data, y_data, z_data, s_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    z_transf_expr = args.z_transf_expr
    s_transf_expr = args.s_transf_expr
    # @todo: add the x,y,z,s variables to a dictionary of allowed arguments 
    #        to eval()
    x = x_data
    y = y_data
    z = z_data
    s = s_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if z_transf_expr != "":
        z_data = eval(z_transf_expr)
    if s_transf_expr != "":
        s_data = eval(s_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]
    if not z_range:
        z_range = [np.min(z_data), np.max(z_data)]

    # Adjust ranges to make sure points on the boundary are displayed
    x_range = utils.nudge_bounds_to_include_boundary_points(x_range)
    y_range = utils.nudge_bounds_to_include_boundary_points(y_range)

    # Get z max and minimum
    z_min, z_max = z_range

    # Get max/min (x,y,z,s) point
    maxmin_index = 0
    if s_type == "max":
        maxmin_index = np.argmax(s_data)
    elif s_type == "min":
        maxmin_index = np.argmin(s_data)

    xyzs_maxmin = (
        x_data[maxmin_index], 
        y_data[maxmin_index], 
        z_data[maxmin_index], 
        s_data[maxmin_index]
    )

    # Cap z data at range limits
    extend_cbar_up = False
    if np.max(z_data) > z_max:
        z_data[z_data > z_max] = z_max
        extend_cbar_up = True
    extend_cbar_down = False
    if np.min(z_data) < z_min:
        z_data[z_data < z_min] = z_min
        extend_cbar_down = True

    # Set color limits
    color_z_lims = list(np.linspace(z_min, z_max, len(ccs.ccodes)+1))

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_maxmin(
        x_data, y_data, z_data, xy_bins, x_range, y_range, s_data, s_type)


    #
    # Generate string to be printed
    #

    # Define a function that returns the color code and marker for any bin 
    # coordinate xiyi in the plot
    def get_ccode_and_marker(xiyi):
        """Determines the color code and marker for a 2D plot bin.

        It normalizes the bin's `z_val` (selected max/min value from
        `bins_info`) using `z_min` and `z_max`. This normalized value,
        along with `color_z_lims`, selects a color from `ccs.ccodes`.
        If the point corresponds to the overall maximum (when `s_type`
        is "max") or minimum (when `s_type` is "min") s-value, and
        `highlight_maxmin_point` is True, it uses a special marker
        (`ms.special_marker`) and color (`ccs.max_bin_ccode`). Otherwise,
        it uses `ms.regular_marker`.

        This function relies on `bins_info`, `z_min`, `z_max`, `s_type`,
        `highlight_maxmin_point`, `color_z_lims`, `ccs` (CCodeSettings),
        and `ms` (MarkerSettings) from the outer scope.

        Args:
            xiyi (tuple): The (x_bin_index, y_bin_index) coordinates
                of the bin.

        Returns:
            tuple: `(ccode, marker)` where `ccode` is the color code (int)
                and `marker` is the string for the plot marker.
        """

        z_val = bins_info[xiyi][2]
        z_norm = 0.0
        if (z_max != z_min):
            z_norm = (z_val - z_min) / (z_max - z_min)

        # Set color code
        ccode = None
        if (z_norm == 1.0) and (s_type == "max"):
            if highlight_maxmin_point:
                ccode = ccs.max_bin_ccode
            else:
                ccode = ccs.ccodes[-1]
        elif (z_norm == 0.0) and (s_type == "max"):
            ccode = ccs.ccodes[0]
        elif (z_norm == 1.0) and (s_type == "min"):
            ccode = ccs.ccodes[-1]
        elif (z_norm == 0.0) and (s_type == "min"):
            if highlight_maxmin_point:
                ccode = ccs.max_bin_ccode
            else:
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
        marker = None
        if highlight_maxmin_point and (z_norm == 1.0) and (s_type == "max"):
            marker = ms.special_marker
        elif highlight_maxmin_point and (z_norm == 0.0) and (s_type == "min"):
            marker = ms.special_marker
        else:
            marker = ms.regular_marker

        return ccode, marker


    # Pass the above function to utils.fill_plot, receive back the generated
    # plot (including axes) as a list of strings.
    plot_lines, fig_width = utils.fill_plot(xy_bins, bins_info, x_bin_limits,
                                            y_bin_limits, ccs, ms, 
                                            get_ccode_and_marker, ff,
                                            add_y_grid_lines=False)


    #
    # Add colorbar, legend, etc
    #

    plot_lines, fig_width = utils.generate_colorbar(plot_lines, fig_width, ff,
                                                    ccs, color_z_lims,
                                                    extend_up=extend_cbar_up,
                                                    extend_down=extend_cbar_down) 

    # max/min legend
    point_str = ""
    if s_index != z_index:
        point_str = "sort_" + s_type + " point: (x, y, z, sort) = "
    else:
        point_str = "z_" + s_type + " point: (x, y, z) = "

    legend_maxmin_entries = []

    marker_str = ""
    if (highlight_maxmin_point) and (s_index == z_index): 
        marker_str = "" + ms.special_marker.strip()

    if s_index != z_index:
        point = ("(" + ff2 + ", " + ff2 + ", " + ff2 + ", " + ff2 + ")").format(
            xyzs_maxmin[0], xyzs_maxmin[1], xyzs_maxmin[2], xyzs_maxmin[3])
    else:
        point = ("(" + ff2 + ", " + ff2 + ", " + ff2 + ")").format(
            xyzs_maxmin[0], xyzs_maxmin[1], xyzs_maxmin[2])

    point_str += point
    legend_maxmin_entries.append(
        (marker_str, ccs.fg_ccode, point_str, ccs.fg_ccode))
    legend_maxmin, legend_maxmin_width = utils.generate_legend(
        legend_maxmin_entries, ccs.bg_ccode, sep="  ", internal_sep=" ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, 
                                              ccs.fg_ccode, ccs.bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend_maxmin,
                                              legend_maxmin_width, plot_lines,
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
    z_label = z_name
    s_label = s_name


    #
    # Add info text
    #

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff=ff2, 
        x_label=x_label, x_range=x_range, x_bin_width=dx, 
        y_label=y_label, y_range=y_range, y_bin_width=dy,
        z_label=z_label, z_range=z_range, 
        s_label=s_label, s_type=s_type,
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        z_transf_expr=z_transf_expr, s_transf_expr=s_transf_expr,
        filter_names=filter_names, mode_name=mode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
