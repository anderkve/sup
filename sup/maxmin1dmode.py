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

regular_marker_up = " ▀"
# regular_marker_up = " █"
regular_marker_down = " ▄"

# regular_marker = " ●"
# regular_marker = " ▁"
# regular_marker = " ▔"

special_marker = " 🟊"  # " ★" " 🟊" " ✱"

fill_marker = "  "
# fill_marker = " ■"
# fill_marker = " █"

empty_bin_marker_grayscale = "  "
# empty_bin_marker_grayscale = " ▁"
# empty_bin_marker_grayscale = " □"
# empty_bin_marker_grayscale = " ■"
empty_bin_marker_color = "  "
# empty_bin_marker_color = " ▁"
# empty_bin_marker_color = " □"
# empty_bin_marker_color = " ■"
empty_bin_marker = empty_bin_marker_color

empty_bin_ccode_grayscale_bb = 235
empty_bin_ccode_grayscale_wb = 253
empty_bin_ccode_grayscale = empty_bin_ccode_grayscale_bb

empty_bin_ccode_color_bb = 235
empty_bin_ccode_color_wb = 253
empty_bin_ccode = empty_bin_ccode_color_bb

max_bin_ccode_grayscale_bb = 231
max_bin_ccode_grayscale_wb = 232
max_bin_ccode_grayscale = max_bin_ccode_grayscale_bb

max_bin_ccode_color_bb = 231
max_bin_ccode_color_wb = 232
max_bin_ccode = max_bin_ccode_color_bb

fill_bin_ccode_grayscale_bb = empty_bin_ccode_grayscale_bb
fill_bin_ccode_grayscale_wb = empty_bin_ccode_grayscale_wb
fill_bin_ccode_grayscale = empty_bin_ccode_grayscale_bb

fill_bin_ccode_color_bb = empty_bin_ccode_color_bb
fill_bin_ccode_color_wb = empty_bin_ccode_color_wb
fill_bin_ccode = fill_bin_ccode_color_bb

ccode_grayscale_bb = 231
ccode_grayscale_wb = 232
ccode_grayscale = ccode_grayscale_bb

ccode_color_bb = 6  # 231
ccode_color_wb = 14 # 232
ccode = ccode_color_bb

def get_color_code(z_val):

    if z_val in [1,2]:
        return ccode
    elif z_val == -1:
        return fill_bin_ccode
    elif z_val == 0:
        return empty_bin_ccode
    else:
        raise Exception("Unexpected z_val. This shouldn't happen...")


def get_marker(z_val):

    if z_val == 2:
        return regular_marker_up
    elif z_val == 1:
        return regular_marker_down
    elif z_val == -1:
        return fill_marker
    elif z_val == 0:
        return empty_bin_marker
    else:
        raise Exception("Unexpected z_val. This shouldn't happen...")


#
# Run
#

def run_max(args):
    run(args, "max")

def run_min(args):
    run(args, "min")

def run(args, mode):

    assert mode in ["max", "min"]

    global ccode
    global ccode_grayscale 
    global bg_ccode
    global fg_ccode
    global max_bin_ccode
    global max_bin_ccode_grayscale
    global empty_bin_ccode
    global empty_bin_ccode_grayscale
    global fill_bin_ccode
    global fill_bin_ccode_grayscale
    global empty_bin_marker
    global special_marker
    global ff
    global ff2

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index

    s_index = args.y_index
    if args.s_index is not None:
        s_index = args.s_index
    s_type = mode

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    use_white_bg = args.use_white_bg
    if use_white_bg:
        bg_ccode = bg_ccode_wb
        fg_ccode = fg_ccode_wb
        empty_bin_ccode = empty_bin_ccode_color_wb
        max_bin_ccode = max_bin_ccode_color_wb
        fill_bin_ccode = fill_bin_ccode_color_wb
        ccode = ccode_color_wb

    if args.use_grayscale:
        if use_white_bg:
            ccode = ccode_grayscale_wb
            max_bin_ccode = max_bin_ccode_grayscale_wb
            empty_bin_ccode = empty_bin_ccode_grayscale_wb
            fill_bin_ccode = fill_bin_ccode_grayscale_wb
        else:
            ccode = ccode_grayscale_bb
            max_bin_ccode = max_bin_ccode_grayscale_bb
            empty_bin_ccode = empty_bin_ccode_grayscale_bb
            fill_bin_ccode = fill_bin_ccode_grayscale_bb
        empty_bin_marker = empty_bin_marker_grayscale

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
    s_name = dset_names[s_index]

    x_data = np.array(f[x_name])[read_slice]
    y_data = np.array(f[y_name])[read_slice]
    s_data = np.array(f[s_name])[read_slice]

    filter_names, filter_datasets = utils.get_filters_hdf5(f, filter_indices, read_slice=read_slice)

    f.close()

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(s_data)
    # data_length = len(x_data)

    if use_filters:
        x_data, y_data, s_data = utils.apply_filters([x_data, y_data, s_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    s_transf_expr = args.s_transf_expr

    # Need this declaration such the 'x' can be used in the eval input string
    x = x_data
    y = y_data
    s = s_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if s_transf_expr != "":
        s_data = eval(s_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]

    # Get max/min point
    maxmin_index = 0
    if s_type == "max":
        maxmin_index = np.argmax(s_data)
    elif s_type == "min":
        maxmin_index = np.argmin(s_data)

    xys_maxmin = (x_data[maxmin_index], y_data[maxmin_index], s_data[maxmin_index])

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_maxmin_1d(x_data, y_data, xy_bins, x_range, y_range, s_data, s_type, fill_below=False, split_marker=True)


    #
    # Generate string to be printed
    #

    plot_lines = []
    fig_width = 0
    for yi in range(xy_bins[1]):

        yi_line = utils.prettify(" ", fg_ccode, bg_ccode)

        for xi in range(xy_bins[0]):

            xiyi = (xi,yi)

            cc = empty_bin_ccode
            marker = empty_bin_marker

            if xiyi in bins_info.keys():
                z_val = bins_info[xiyi][2]

                cc = get_color_code(z_val)
                marker = get_marker(z_val)

            # Add point to line
            yi_line += utils.prettify(marker, cc, bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 5 + len(ff.format(0))
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, fg_ccode, bg_ccode, bold=True)
    fill_mod_func = lambda input_str : utils.prettify(input_str, empty_bin_ccode, bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=axes_mod_func, mod_func_2=fill_mod_func, floatf=ff, add_y_grid_lines=True)

    # Add blank top line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode, insert_pos=0)


    #
    # Add legend
    #

    # max/min legend
    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(input_str, input_fg_ccode, bg_ccode, bold=True)

    point_str = ""
    if s_index != y_index:
        point_str = "sort_" + s_type + " point: (x, y, sort) = "
    else:
        point_str = "y_" + s_type + " point: (x, y) = "

    legend_maxmin_entries = []

    marker_str = ""

    if s_index != y_index:
        point = ("(" + ff2 + ", " + ff2 + ", " + ff2 + ")").format(xys_maxmin[0], xys_maxmin[1], xys_maxmin[2])
    else:
        point = ("(" + ff2 + ", " + ff2 + ")").format(xys_maxmin[0], xys_maxmin[1])

    point_str += point
    legend_maxmin_entries.append( (marker_str, fg_ccode, point_str, fg_ccode) )
    legend_maxmin, legend_maxmin_width = utils.generate_legend(legend_maxmin_entries, legend_mod_func, sep="  ", internal_sep=" ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend_maxmin, legend_maxmin_width, plot_lines, fig_width, fg_ccode, bg_ccode)


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
    s_label = s_name


    #
    # Add info text
    #

    info_lines = utils.generate_info_text(ff2,
                                          x_label, x_range, 
                                          y_label=y_label, y_range=y_range, 
                                          # z_label=z_label, z_range=z_range, 
                                          s_label=s_label, s_type=s_type,
                                          x_transf_expr=x_transf_expr, 
                                          y_transf_expr=y_transf_expr,
                                          s_transf_expr=s_transf_expr,
                                          # capped_z=use_capped_loglike,
                                          # capped_label="ln(L)",
                                          # cap_val=args.cap_loglike_val,
                                          filter_names=filter_names,
                                          mode_name=mode,
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
