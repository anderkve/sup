# -*- coding: utf-8 -*-

"""sup.plr2dmode

A sup run mode that produces a 2d map of the profile likelihood ratio, 
L(x,y)/L_max(x,y), across the (x,y) plane.

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'plr2d' run mode.

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
    loglike_index = args.loglike_index
    s_index = args.loglike_index
    s_type = "max"

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    use_capped_loglike = False
    if args.cap_loglike_val is not None:
        use_capped_loglike = True

    color_z_lims = [0.0, 0.003, 0.046, 0.317]

    ccs = CCodeSettings()
    ccs.cmaps["color_bb"] = [236, 19, 45, 226]
    ccs.cmaps["color_wb"] = [248, 19, 45, 220]
    ccs.cmaps["grayscale_bb"] = [233, 237, 242, 231]
    ccs.cmaps["grayscale_wb"] = [254, 250, 243, 232]
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.use_n_colors = len(color_z_lims)
    ccs.update()

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_2d

    highlight_maxlike_point = not(args.no_star)

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    dsets, dset_names = utils.read_input_file(
        input_file, [x_index, y_index, loglike_index, s_index], read_slice, 
        delimiter=args.delimiter)
    x_data, y_data, loglike_data, s_data = dsets
    x_name, y_name, loglike_name, s_name = dset_names

    filter_datasets, filter_names = utils.get_filters(input_file, 
                                                      filter_indices, 
                                                      read_slice=read_slice, 
                                                      delimiter=args.delimiter)

    if use_filters:
        x_data, y_data, loglike_data, s_data = utils.apply_filters(
            [x_data, y_data, loglike_data, s_data], filter_datasets)

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

    # if not z_min:
    #     z_min = np.min(z_data)
    # if not z_max:
    #     z_max = np.max(z_data)

    # Cap loglike?
    if use_capped_loglike:
        loglike_data = np.minimum(loglike_data, args.cap_loglike_val)


    #
    # Create likelihood ratio dataset
    #

    loglike_max = np.max(loglike_data)
    likelihood_ratio = np.exp(loglike_data) / np.exp(loglike_max)

    z_data = likelihood_ratio
    # z_min = np.min(z_data)
    # z_max = np.max(z_data)
    # z_range = [z_min, z_max]

    s_data = z_data  # sort according to likelihood_ratio


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

        z_val = bins_info[xiyi][2]
        z_norm = z_val

        # Set color code
        ccode = None
        if z_norm == 1.0:
            if use_capped_loglike or (not highlight_maxlike_point):
                ccode = ccs.ccodes[-1]
            else:
                ccode = ccs.max_bin_ccode
        else:
            i = 0
            for j, lim in enumerate(color_z_lims):
                if z_norm > lim:
                    i = j
                else:
                    break
            ccode = ccs.ccodes[i]

        # Set marker
        marker = None
        if z_norm == 1.0:
            if use_capped_loglike or (not highlight_maxlike_point):
                marker = ms.regular_marker
            else:
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
    # Add legend
    #

    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(
        input_str, input_fg_ccode, ccs.bg_ccode, bold=True)
    legend_entries = []

    # legend_entries.append(("", ccs.fg_ccode, "", ccs.fg_ccode))
    if (not use_capped_loglike) and highlight_maxlike_point:
        legend_entries.append((ms.special_marker.strip(), ccs.max_bin_ccode, 
                               "best-fit", ccs.fg_ccode))
    legend_entries.append((ms.regular_marker.strip(), ccs.ccodes[-1], "1σ",
                           ccs.fg_ccode))
    legend_entries.append((ms.regular_marker.strip(), ccs.ccodes[-2], "2σ",
                           ccs.fg_ccode))
    legend_entries.append((ms.regular_marker.strip(), ccs.ccodes[-3], "3σ",
                           ccs.fg_ccode))
    
    legend, legend_width = utils.generate_legend(legend_entries,
                                                 legend_mod_func,
                                                 sep="  ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, 
                                              ccs.fg_ccode, ccs.bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend, legend_width, plot_lines,
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
    s_label = "likelihood ratio, L(x,y)/L_max"


    #
    # Add info text
    #

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff2,
        x_label, x_range, x_bin_width=dx, 
        y_label=y_label, y_range=y_range, y_bin_width=dy,
        s_label=s_label, s_type=s_type,
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        capped_z=use_capped_loglike, capped_label="ln(L)",
        cap_val=args.cap_loglike_val,
        filter_names=filter_names,
        mode_name="profile likelihood ratio, L/L_max")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
