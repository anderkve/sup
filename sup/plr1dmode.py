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

    input_file = args.input_file
    x_index = args.x_index
    # y_index = args.y_index
    loglike_index = args.loglike_index
    s_index = args.loglike_index
    s_type = "max"

    confidence_levels = args.confidence_levels
    if not confidence_levels:
        confidence_levels = [68.3, 95.45]

    confidence_levels = np.array(confidence_levels)
    if np.any(confidence_levels>100.0):
        raise SupRuntimeError("Can't use a confidence level of more than 100%.")
    elif np.any(confidence_levels<=0.0):
        raise SupRuntimeError("Can't use a confidence level of <= 0%.")

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

    ccs = CCodeSettings()
    ccs.graph_ccodes["grayscale_bb"] = 231
    ccs.graph_ccodes["grayscale_wb"] = 232
    ccs.graph_ccodes["color_bb"] = 1
    ccs.graph_ccodes["color_wb"] = 9
    ccs.bar_ccodes_lists["grayscale_bb"] = [243, 240]
    ccs.bar_ccodes_lists["grayscale_wb"] = [243, 240]
    ccs.bar_ccodes_lists["color_bb"] = [3,11]
    ccs.bar_ccodes_lists["color_wb"] = [3,11]
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

    dsets, dset_names = utils.read_input_file(input_file,
                                              [x_index, loglike_index, s_index],
                                              read_slice, 
                                              delimiter=args.delimiter)
    x_data, loglike_data, s_data = dsets
    x_name, loglike_name, s_name = dset_names

    filter_datasets, filter_names = utils.get_filters(input_file,
                                                      filter_indices,
                                                      read_slice=read_slice,
                                                      delimiter=args.delimiter)

    if use_filters:
        x_data, loglike_data, s_data = utils.apply_filters(
            [x_data, loglike_data, s_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    # y_transf_expr = args.y_transf_expr

    # Need this declaration such the 'x' can be used in the eval input string
    x = x_data
    # y = y_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    # if y_transf_expr != "":
    #     y_data = eval(y_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [0.0, 1.0]

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

    y_data = likelihood_ratio
    s_data = y_data  # sort according to likelihood_ratio


    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits, x_func_data, y_func_data = \
        utils.get_bin_tuples_maxmin_1d(x_data, y_data, xy_bins, x_range, 
                                       y_range, s_data, s_type, 
                                       split_marker=True, 
                                       return_function_data=True, 
                                       fill_y_val=np.nan)


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
            marker = ms.empty_bin_marker

            if xiyi in bins_info.keys():
                z_val = bins_info[xiyi][2]

                ccode = get_color_code(ccs, z_val)
                marker = get_marker(ms, z_val)

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
    # Add horizontal confidence interval bars
    #

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode)

    cl_bar_lines = utils.generate_confidence_level_bars(confidence_levels, 
                                                        y_func_data, 
                                                        x_bin_limits, ff2)

    for i,line in enumerate(cl_bar_lines):
        cl_bar_width = len(line)
        cl_bar = utils.prettify(line, ccs.bar_ccodes[i % 2], ccs.bg_ccode)
        plot_lines, fig_width = utils.insert_line(cl_bar, cl_bar_width, 
                                                  plot_lines, fig_width,
                                                  ccs.fg_ccode, ccs.bg_ccode)


    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


    #
    # Set labels
    #

    x_label = x_name
    y_label = "likelihood ratio, L(x)/L_max"
    s_label = y_label


    #
    # Add info text
    #

    dx = x_bin_limits[1] - x_bin_limits[0]

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff2, 
        x_label, x_range, x_bin_width=dx, 
        y_label=y_label, y_range=y_range, 
        s_label=s_label, s_type=s_type,
        x_transf_expr = x_transf_expr, 
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
