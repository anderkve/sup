# -*- coding: utf-8 -*-

"""sup.chisq2dmode

A sup run mode that produces a 2d map of the delta chi-square,
chi^2(x,y) - chi^2_min, across the (x,y) plane, showing the minimum delta chi-square in each bin.
Assumes the input data contains log-likelihood values, from which chi-square is computed.
"""

import numpy as np
from scipy.stats import chi2
import sup.defaults as defaults
import sup.utils as utils
import sup.colors as colors
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'chisq2d' run mode.

    This function
    - interprets the command-line arguments for this run mode;
    - reads and processes the data as appropriate for this run mode (delta chi-square plots);
    - constructs the full output as a list of strings; and
    - prints the output to screen.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    
    """

    input_file = args.input_file
    x_index = args.x_index
    y_index = args.y_index
    chisq_index = args.chisq_index
    s_index = args.chisq_index
    s_type = "min"

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    ccs = CCodeSettings()
    
    ccs.cmaps["color_bb"] = colors.cmaps[args.cmap_index]
    ccs.cmaps["color_wb"] = colors.cmaps[args.cmap_index]
    ccs.cmaps["grayscale_bb"] = [233, 237, 242, 231]
    ccs.cmaps["grayscale_wb"] = [254, 250, 243, 232]
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.use_n_colors = args.n_colors
    ccs.update()

    if args.reverse_colormap:
        ccs.ccodes = ccs.ccodes[::-1]

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_2d

    highlight_minchisq_point = not(args.no_star)

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    dsets, dset_names = utils.read_input_file(
        args.input_file, [x_index, y_index, chisq_index, s_index], read_slice, 
        delimiter=args.delimiter, stdin_format=args.stdin_format)
    x_data, y_data, chisq_data, s_data = dsets
    x_name, y_name, chisq_name, s_name = dset_names

    filter_datasets, filter_names = utils.get_filters(args.input_file, 
                                                      filter_indices, 
                                                      read_slice=read_slice, 
                                                      delimiter=args.delimiter,
                                                      stdin_format=args.stdin_format)

    if use_filters:
        x_data, y_data, chisq_data, s_data = utils.apply_filters(
            [x_data, y_data, chisq_data, s_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
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
    # Create delta chi-square dataset
    #

    delta_chisq_data = chisq_data - np.min(chisq_data)
    z_data = delta_chisq_data
    s_data = z_data  # sort according to delta_chisq_data

    # Get z max and min
    z_min, z_max = args.z_range

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
        """Determines the color code and marker for a 2D delta chi-square plot bin.

        The `z_val` (minimum delta chi-square in the bin from `bins_info`) is used.
        If `z_val` corresponds to the minimum possible delta chi-square (typically 0.0, or `z_min`),
        and `highlight_minchisq_point` is True, it uses `ccs.max_bin_ccode` and `ms.special_marker`.
        Otherwise, `z_val` is compared against `color_z_lims` (derived from the
        range of `delta_chisq_data` or `args.z_range`) to select a color from `ccs.ccodes`,
        and `ms.regular_marker` is used.

        This function relies on `bins_info`, `color_z_lims`, `z_min`,
        `highlight_minchisq_point`, `ccs` (CCodeSettings), and `ms` (MarkerSettings) 
        from the outer scope.

        Args:
            xiyi (tuple): The (x_bin_index, y_bin_index) coordinates
                of the bin.

        Returns:
            tuple: `(ccode, marker)` where `ccode` is the color code (int)
                and `marker` is the string for the plot marker.
        """

        z_val = bins_info[xiyi][2]

        # Set marker and color code
        is_best_fit_point = (z_val == z_min)

        if is_best_fit_point and highlight_minchisq_point:
            ccode = ccs.max_bin_ccode
            marker = ms.special_marker
        else:
            marker = ms.regular_marker
            # Determine color based on z_val and color_z_lims
            # color_z_lims are lower bounds of intervals.
            # ccs.ccodes[i] is for z_val in [color_z_lims[i], color_z_lims[i+1])
            # The last color is for z_val >= color_z_lims[-1]
            
            selected_idx = 0
            # Iterate up to the second to last limit.
            # If z_val is below color_z_lims[0], it gets ccs.ccodes[0].
            # This handles cases where z_val might be less than z_min due to args.z_range.
            if len(color_z_lims) == 1: # Only one limit, so only one color
                 selected_idx = 0
            elif z_val < color_z_lims[0] :
                 selected_idx = 0 # Should not happen if z_min is the first limit and z_val >= z_min
            else:
                for j, lim_val in enumerate(color_z_lims):
                    if z_val >= lim_val:
                        selected_idx = j
                    else:
                        # z_val is less than current lim_val, so it belonged to previous segment
                        break 
            if selected_idx >= ccs.use_n_colors:
                selected_idx = ccs.use_n_colors - 1

            # print(f"DEBUG: xiyi: {xiyi}  selected_idx: {selected_idx}  ccs.ccodes: {ccs.ccodes}")
            ccode = ccs.ccodes[selected_idx]

        return ccode, marker


    # Pass the above function to utils.fill_plot, receive back the generated
    # plot (including axes) as a list of strings.
    plot_lines, fig_width = utils.fill_plot(xy_bins, bins_info, x_bin_limits,
                                            y_bin_limits, ccs, ms, 
                                            get_ccode_and_marker, ff,
                                            add_y_grid_lines=False)


    #
    # Add legend
    #

    legend_entries = []

    if highlight_minchisq_point:
        legend_entries.append((ms.special_marker.strip(), ccs.max_bin_ccode,
                               "best-fit (min chi^2)", ccs.fg_ccode))

    # Legend entries for delta chi-square ranges could be added here if desired,
    # similar to hist2dmode's legend. Example
    # if len(color_z_lims) > 1:
    #     for i in range(ccs.use_n_colors):
    #         lower_bound = color_z_lims[i]
    #         upper_bound_str = f"{color_z_lims[i+1]}" if i < ccs.use_n_colors - 1 else f"{z_max}"
    #         legend_entries.append((ms.regular_marker.strip(), ccs.ccodes[i],
    #                                f"[{lower_bound:.1f}, {upper_bound_str})", ccs.fg_ccode))
    # else: # Single color case
    #    legend_entries.append((ms.regular_marker.strip(), ccs.ccodes[0],
    #                            f"~{color_z_lims[0]:.1f}", ccs.fg_ccode))

    legend, legend_width = utils.generate_legend(legend_entries,
                                                 ccs.bg_ccode,
                                                 sep="  ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, 
                                              ccs.fg_ccode, ccs.bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend, legend_width, plot_lines,
                                              fig_width, ccs.fg_ccode,
                                              ccs.bg_ccode)


    #
    # Add colorbar
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

    x_label = x_name
    y_label = y_name
    s_label = "delta chi-square, chi^2 - chi^2_min"


    #
    # Add info text
    #

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff=ff2,
        x_label=x_label, x_range=x_range, x_bin_width=dx, 
        y_label=y_label, y_range=y_range, y_bin_width=dy,
        s_label=s_label, s_type=s_type,
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        filter_names=filter_names,
        mode_name="delta chi-square, chi^2 - chi^2_min")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
