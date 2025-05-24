# -*- coding: utf-8 -*-

"""sup.graph2dmode

A sup run mode that produces a 2d map of a function z = f(x,y).

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
import sup.colors as colors
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'graph2d' run mode.

    This function 
    - interprets the command-line arguments for this run mode;
    - generates data from the provided function definition;
    - constructs the full output as a list of strings; and
    - prints the output to screen.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    
    """

    function_str = args.function

    x_range = args.x_range
    y_range = args.y_range
    z_range = args.z_range

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

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]
    if not z_range:
        z_range = [np.min(z_data), np.max(z_data)]

    z_min, z_max = z_range

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

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg(
        x_data, y_data, z_data, xy_bins, x_range, y_range)


    #
    # Generate string to be printed
    #

    # Define a function that returns the color code and marker for any bin 
    # coordinate xiyi in the plot
    def get_ccode_and_marker(xiyi):
        """Determines the color code and marker for a plot bin.

        The function value f(x,y) for the bin center (`z_val`, obtained
        from `bins_info`) is used to select a color from `ccs.ccodes`.
        The selection is based on where `z_val` falls within the
        intervals defined by `color_z_lims`. The marker is always
        `ms.regular_marker`.

        This function relies on `bins_info`, `color_z_lims`,
        `ccs` (CCodeSettings), and `ms` (MarkerSettings) from the
        outer scope.

        Args:
            xiyi (tuple): The (x_bin_index, y_bin_index) coordinates
                of the bin.

        Returns:
            tuple: A tuple `(ccode, marker)` where `ccode` is the color
                code (int) and `marker` is `ms.regular_marker`.
        """

        z_val = bins_info[xiyi][2]

        # Set color code
        ccode = None
        if z_val >= color_z_lims[-1]:
            ccode = ccs.ccodes[-1]
        elif z_val <= color_z_lims[0]:
            ccode = ccs.ccodes[0]        
        else:
            i = 0
            for j, lim in enumerate(color_z_lims):
                if z_val > lim:
                    i = j
                else:
                    break
            ccode = ccs.ccodes[i]

        # Set marker
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

        
    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


    #
    # Set labels
    #

    x_label = "x"
    y_label = "y"
    z_label = "f(x,y) = " + function_str


    #
    # Add info text
    #

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff=ff2, 
        x_label=x_label, x_range=x_range, y_label=y_label, y_range=y_range, 
        z_label=z_label, z_range=z_range, mode_name="graph")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
