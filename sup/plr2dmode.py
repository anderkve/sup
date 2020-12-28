import sys
import numpy as np
import h5py
import sup.defaults as defaults
import sup.utils as utils


#
# Variables for colors, markers, padding, etc
#

ff = defaults.ff
ff2 = defaults.ff2
left_padding = 2*" "

bg_ccode_bb, fg_ccode_bb = 16, 231  # 232, 231
bg_ccode_wb, fg_ccode_wb = 231, 16  # 231, 232
bg_ccode = bg_ccode_bb
fg_ccode = fg_ccode_bb

regular_marker = " ■"
special_marker = " 🟊"  # " ★" " 🟊" " ✱"

empty_bin_marker_grayscale = " □"
empty_bin_marker_color = " ■"
empty_bin_marker = empty_bin_marker_color

empty_bin_ccode_grayscale_bb = 233
empty_bin_ccode_grayscale_wb = 254
empty_bin_ccode_grayscale = empty_bin_ccode_grayscale_bb

empty_bin_ccode_color_bb = 233
empty_bin_ccode_color_wb = 255
empty_bin_ccode = empty_bin_ccode_color_bb

max_bin_ccode_grayscale_bb = 231
max_bin_ccode_grayscale_wb = 232
max_bin_ccode_grayscale = max_bin_ccode_grayscale_bb

max_bin_ccode_color_bb = 231
max_bin_ccode_color_wb = 232
max_bin_ccode = max_bin_ccode_color_bb

ccodes_grayscale_bb = [233, 237, 242, 231]
ccodes_grayscale_wb = [254, 250, 243, 232]
ccodes_grayscale = ccodes_grayscale_bb

ccodes_color_bb = [236, 19, 45, 226]
ccodes_color_wb = [248, 19, 45, 220]
ccodes = ccodes_color_bb

color_z_lims = [0.0, 0.003, 0.046, 0.317]

def get_color_code(z_norm, highlight_maxlike_point, use_capped_loglike=False):

    if z_norm == 1.0:
        if use_capped_loglike or (not highlight_maxlike_point):
            return ccodes[-1]
        else:
            return max_bin_ccode

    i = 0
    for j, lim in enumerate(color_z_lims):
        if z_norm > lim:
            i = j
        else:
            break
    return ccodes[i]


def get_marker(z_norm, highlight_maxlike_point, use_capped_loglike=False):

    if z_norm == 1.0:
        if use_capped_loglike or (not highlight_maxlike_point):
            return regular_marker
        else:
            return special_marker
    else:
        return regular_marker


#
# Run
#

def run(args):

    global ccodes 
    global ccodes_grayscale 
    global bg_ccode
    global fg_ccode
    global max_bin_ccode
    global max_bin_ccode_grayscale
    global empty_bin_ccode
    global empty_bin_ccode_grayscale
    global empty_bin_marker
    global special_marker
    global ff
    global ff2

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

    # z_min = defaults.z_min
    # z_max = defaults.z_max

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    use_capped_loglike = False
    if args.cap_loglike_val is not None:
        use_capped_loglike = True

    use_white_bg = args.use_white_bg
    if use_white_bg:
        bg_ccode = bg_ccode_wb
        fg_ccode = fg_ccode_wb
        empty_bin_ccode = empty_bin_ccode_color_wb
        max_bin_ccode = max_bin_ccode_color_wb
        ccodes = ccodes_color_wb

    if args.use_grayscale:
        if use_white_bg:
            ccodes = ccodes_grayscale_wb
            max_bin_ccode = max_bin_ccode_grayscale_wb
            empty_bin_ccode = empty_bin_ccode_grayscale_wb
        else:
            ccodes = ccodes_grayscale_bb
            max_bin_ccode = max_bin_ccode_grayscale_bb
            empty_bin_ccode = empty_bin_ccode_grayscale_bb
        empty_bin_marker = empty_bin_marker_grayscale

    highlight_maxlike_point = not(args.no_star)

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    f = h5py.File(input_file, "r")

    dset_names = utils.get_dataset_names(f)
    x_name = dset_names[x_index]
    y_name = dset_names[y_index]
    loglike_name = dset_names[loglike_index]
    s_name = dset_names[s_index]

    x_data = np.array(f[x_name])[read_slice]
    y_data = np.array(f[y_name])[read_slice]
    loglike_data = np.array(f[loglike_name])[read_slice]
    s_data = np.array(f[s_name])[read_slice]

    filter_names, filter_datasets = utils.get_filters_hdf5(f, filter_indices, read_slice=read_slice)

    f.close()

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(loglike_data)
    assert len(x_data) == len(s_data)
    # data_length = len(x_data)

    if use_filters:
        x_data, y_data, loglike_data, s_data = utils.apply_filters([x_data, y_data, loglike_data, s_data], filter_datasets)

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

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_maxmin(x_data, y_data, z_data, xy_bins, x_range, y_range, s_data, s_type)


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
                z_norm = z_val
                # z_norm = (z_val - z_min) / (z_max - z_min)

                ccode = get_color_code(z_norm, highlight_maxlike_point, use_capped_loglike=use_capped_loglike)
                marker = get_marker(z_norm, highlight_maxlike_point, use_capped_loglike=use_capped_loglike)

            # Add point to line
            yi_line += utils.prettify(marker, ccode, bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 5 + len(ff.format(0))
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, fg_ccode, bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=axes_mod_func, floatf=ff)

    # Add blank top line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode, insert_pos=0)


    #
    # Add legend
    #

    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(input_str, input_fg_ccode, bg_ccode, bold=True)
    legend_entries = []

    # legend_entries.append( ("", fg_ccode, "", fg_ccode) )
    if (not use_capped_loglike) and highlight_maxlike_point:
        legend_entries.append( (special_marker.strip(), max_bin_ccode, "best-fit", fg_ccode) )
    legend_entries.append( (regular_marker.strip(), ccodes[-1], "1σ", fg_ccode) )
    legend_entries.append( (regular_marker.strip(), ccodes[-2], "2σ", fg_ccode) )
    legend_entries.append( (regular_marker.strip(), ccodes[-3], "3σ", fg_ccode) )
    
    legend, legend_width = utils.generate_legend(legend_entries, legend_mod_func, sep="  ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend, legend_width, plot_lines, fig_width, fg_ccode, bg_ccode)


    #
    # Add left padding
    #

    for i,line in enumerate(plot_lines):
        plot_lines[i] = utils.prettify(left_padding, fg_ccode, bg_ccode) + line


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

    info_lines = utils.generate_info_text(ff2,
                                          x_label, x_range, 
                                          x_bin_width=dx,
                                          y_label=y_label, y_range=y_range, 
                                          y_bin_width=dy,
                                          # z_label=z_label, z_range=z_range, 
                                          s_label=s_label, s_type=s_type,
                                          x_transf_expr=x_transf_expr, 
                                          y_transf_expr=y_transf_expr,
                                          capped_z=use_capped_loglike,
                                          capped_label="ln(L)",
                                          cap_val=args.cap_loglike_val,
                                          filter_names=filter_names,
                                          mode_name="profile likelihood ratio, L/L_max",
                                          left_padding=left_padding + " ")

    for i,line in enumerate(info_lines):
        pretty_line = utils.prettify(line + "  ", fg_ccode, bg_ccode, bold=False)
        plot_lines, fig_width = utils.insert_line(pretty_line, len(line), plot_lines, fig_width, fg_ccode, bg_ccode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    sys.exit()    
