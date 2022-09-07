# -*- coding: utf-8 -*-

"""sup.post1dmode

A sup run mode that produces a 1d posterior distribution for variable x.

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'post1d' run mode.

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

    w_index = args.w_index
    use_weights = bool(w_index is not None)

    normalize_histogram = True

    credible_regions = args.credible_regions
    if not credible_regions:
        credible_regions = [68.3, 95.45]

    credible_regions = np.array(credible_regions)

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
    ccs.graph_ccodes["color_bb"] = 3
    ccs.graph_ccodes["color_wb"] = 11
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.update()

    ms = MarkerSettings()
    ms.regular_marker_up = " █"
    ms.regular_marker_down = " ▄"
    ms.fill_marker = " █"
    ms.empty_bin_marker = defaults.empty_bin_marker_1d

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    x_name = None
    x_data = None
    w_name = None
    w_data = None

    if use_weights:
        dsets, dset_names = utils.read_input_file(input_file,
                                                  [x_index, w_index],
                                                  read_slice,
                                                  delimiter=args.delimiter)
        x_data, w_data = dsets
        x_name, w_name = dset_names
        utils.check_weights(w_data, w_name)
    else:
        dsets, dset_names = utils.read_input_file(input_file, 
                                                  [x_index], 
                                                  read_slice, 
                                                  delimiter=args.delimiter)
        x_data,  = dsets
        x_name,  = dset_names
        w_data = np.ones(len(x_data))

    filter_datasets, filter_names = utils.get_filters(input_file,
                                                      filter_indices,
                                                      read_slice=read_slice,
                                                      delimiter=args.delimiter)

    if use_filters:
        x_data, w_data = utils.apply_filters([x_data, w_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    w_transf_expr = args.w_transf_expr

    # @todo: add the x,y,w variables to a dictionary of allowed arguments 
    #        to eval()
    x = x_data
    w = w_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if w_transf_expr != "":
        w_data = eval(w_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]


    #
    # Get a dict with info per bin
    #

    bins_content_unweighted,_  = np.histogram(x_data, bins=xy_bins[0],
                                              range=x_range, 
                                              density=normalize_histogram) 
    bins_content, x_bin_limits = np.histogram(x_data, bins=xy_bins[0], 
                                              range=x_range, weights=w_data, 
                                              density=normalize_histogram) 

    # Apply y-axis transformation
    bins_content_not_transformed = bins_content
    y = bins_content
    if y_transf_expr != "":
        bins_content = eval(y_transf_expr)

    dx = x_bin_limits[1] - x_bin_limits[0]
    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx

    if not y_range:
        y_range = [
            np.min(bins_content[bins_content > -np.inf]), 
            np.max(bins_content)
        ]
    y_min, y_max = y_range

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg_1d(
        x_bin_centres, np.minimum(bins_content, y_max), xy_bins, x_range,
        y_range, fill_below=True, split_marker=True)


    #
    # Generate string to be printed
    #

    # Define a function that returns the color code and marker for any bin 
    # coordinate xiyi in the plot
    def get_ccode_and_marker(xiyi):

        z_val = bins_info[xiyi][2]

        # Set color code
        ccode = None
        if z_val in [1,2]:
            ccode = ccs.graph_ccode
        elif z_val == -1:
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
        elif z_val == -1:
            marker = ms.fill_marker
        elif z_val == 0:
            marker = ms.empty_bin_marker
        else:
            raise Exception("Unexpected z_val. This shouldn't happen...")

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
    # Add horizontal credible region bars
    #

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode)

    cr_bar_lines = utils.generate_credible_region_bars(
        credible_regions, bins_content_not_transformed, x_bin_limits, ff2)

    for i,line in enumerate(cr_bar_lines):
        cr_bar_width = len(line)
        cr_bar = utils.prettify(line, ccs.bar_ccodes[i % 2], ccs.bg_ccode)
        plot_lines, fig_width = utils.insert_line(cr_bar, cr_bar_width,
                                                  plot_lines, fig_width,
                                                  ccs.fg_ccode, ccs.bg_ccode)


    #
    # Add legend
    #

    # max bin legend
    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(
        input_str, input_fg_ccode, ccs.bg_ccode, bold=True)

    maxbin_index = np.argmax(bins_content)
    maxbin_content = bins_content[maxbin_index]
    maxbin_limits = [x_bin_limits[maxbin_index], x_bin_limits[maxbin_index+1]]
    
    maxbin_str = "max bin:  x: "
    maxbin_str += ("(" + ff2 + ", " + ff2 + ")").format(maxbin_limits[0],
                                                        maxbin_limits[1])
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
    y_label = "bin height"
    w_label = w_name


    #
    # Add info text
    #

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff2,
        x_label, x_range, x_bin_width=dx,
        y_label=y_label, y_range=y_range, 
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        y_normalized_hist=normalize_histogram, 
        w_label=w_label, w_transf_expr=w_transf_expr,
        filter_names=filter_names, mode_name="posterior")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
