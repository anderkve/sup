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

bg_ccode_bb, fg_ccode_bb = 232, 231
bg_ccode_wb, fg_ccode_wb = 231, 232
bg_ccode = bg_ccode_bb
fg_ccode = fg_ccode_bb

regular_marker = " ■"
special_marker = " 🟊"  # " ★" " 🟊" " ✱"

empty_bin_marker_grayscale = " □"
empty_bin_marker_color = " □"
empty_bin_marker = empty_bin_marker_color

empty_bin_ccode_grayscale_bb = 237
empty_bin_ccode_grayscale_wb = 252
empty_bin_ccode_grayscale = empty_bin_ccode_grayscale_bb

empty_bin_ccode_color_bb = 237
empty_bin_ccode_color_wb = 252
empty_bin_ccode = empty_bin_ccode_color_bb

max_bin_ccode_grayscale_bb = 231
max_bin_ccode_grayscale_wb = 232
max_bin_ccode_grayscale = max_bin_ccode_grayscale_bb

max_bin_ccode_color_bb = 231
max_bin_ccode_color_wb = 232
max_bin_ccode = max_bin_ccode_color_bb

cmaps_grayscale = [
    [237, 239, 241, 243, 245, 247, 249, 251, 253, 255],  # for black background
    [235, 237, 239, 241, 243, 245, 247, 249, 251, 253],  # for white background
]
ccodes_grayscale = cmaps_grayscale[0]

cmaps = [
    [53,56,62,26,31,36,42,47,154,226],      # viridis
    [18,20,27,45,122,155,226,214,202,196],  # jet
]
ccodes = cmaps[0]



def get_color_code(z_val, z_norm, color_z_lims, s_type, use_capped_z=False):

    assert s_type in ["min", "max"]

    if (z_norm == 1.0) and (s_type == "max"):
        if use_capped_z:
            return ccodes[-1]
        else:
            return max_bin_ccode
    elif (z_norm == 0.0) and (s_type == "min"):
        if use_capped_z:
            return ccodes[-1]
        else:
            return max_bin_ccode

    i = 0
    for j, lim in enumerate(color_z_lims):
        if z_val >= lim:
            i = j
        else:
            break
    return ccodes[i]


def get_marker(z_norm, s_type, use_capped_z=False):

    assert s_type in ["min", "max"]

    if (z_norm == 1.0) and (s_type == "max"):
        if use_capped_z:
            return regular_marker
        else:
            return special_marker
    elif (z_norm == 0.0) and (s_type == "min"):
        if use_capped_z:
            return regular_marker
        else:
            return special_marker
    else:
        return regular_marker


#
# Run
#

def run_max(args):
    run(args, "max")

def run_min(args):
    run(args, "min")

def run(args, mode):

    assert mode in ["max", "min"]
    assert args.cmap_index in range(len(cmaps))

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
    global color_z_lims

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index
    z_index = args.z_index

    s_index = args.z_index
    if args.s_index is not None:
        s_index = args.s_index
    s_type = mode

    x_range = args.x_range
    y_range = args.y_range

    # z_min = defaults.z_min
    # z_max = defaults.z_max

    read_length = defaults.read_length

    # x_use_abs_val = args.x_use_abs_val
    # y_use_abs_val = args.y_use_abs_val
    # z_use_abs_val = args.z_use_abs_val
    # s_use_abs_val = args.s_use_abs_val
    # if s_index == z_index:
    #     s_use_abs_val = z_use_abs_val

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    use_capped_z = False
    if args.cap_z_val is not None:
        use_capped_z = True

    cmap_index = args.cmap_index
    ccodes = cmaps[cmap_index]
    use_white_bg = args.use_white_bg
    if use_white_bg:
        bg_ccode = bg_ccode_wb
        fg_ccode = fg_ccode_wb
        empty_bin_ccode = empty_bin_ccode_color_wb
        max_bin_ccode = max_bin_ccode_color_wb
        # ccodes = ccodes_color_wb

    if args.use_grayscale:
        if use_white_bg:
            ccodes = cmaps_grayscale[1]
            # ccodes = ccodes_grayscale_wb
            max_bin_ccode = max_bin_ccode_grayscale_wb
            empty_bin_ccode = empty_bin_ccode_grayscale_wb
        else:
            ccodes = cmaps_grayscale[0]
            # ccodes = ccodes_grayscale_bb
            max_bin_ccode = max_bin_ccode_grayscale_bb
            empty_bin_ccode = empty_bin_ccode_grayscale_bb
        empty_bin_marker = empty_bin_marker_grayscale

    n_colors = args.n_colors
    if n_colors < 1:
        n_colors = 1
    elif n_colors > 10:
        n_colors = 10
    ccodes = [ ccodes[int(i)] for i in np.round( np.linspace(0, len(ccodes)-1, n_colors) ) ]

    #
    # Read datasets from file
    #

    f = h5py.File(input_file, "r")

    dset_names = utils.get_dataset_names(f)
    x_name = dset_names[x_index]
    y_name = dset_names[y_index]
    z_name = dset_names[z_index]
    s_name = dset_names[s_index]

    x_data = np.array(f[x_name])[:read_length]
    y_data = np.array(f[y_name])[:read_length]
    z_data = np.array(f[z_name])[:read_length]
    s_data = np.array(f[s_name])[:read_length]

    f.close()

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(z_data)
    assert len(x_data) == len(s_data)
    # data_length = len(x_data)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    z_transf_expr = args.z_transf_expr
    s_transf_expr = args.s_transf_expr
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

    # if x_use_abs_val:
    #     x_data = np.abs(x_data)
    # if y_use_abs_val:
    #     y_data = np.abs(y_data)
    # if z_use_abs_val:
    #     z_data = np.abs(z_data)
    # if s_use_abs_val:
    #     s_data = np.abs(s_data)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]

    # Cap z dataset?
    if use_capped_z:
        z_data = np.minimum(z_data, args.cap_z_val)

    # Get z max and minimum
    z_min = np.min(z_data)
    z_min_index = np.argmin(z_data)
    z_max = np.max(z_data)
    z_max_index = np.argmax(z_data)
    z_range = [z_min, z_max]

    # Get positions of max/min points
    xyz_max = (x_data[z_max_index], y_data[z_max_index], z_max)
    xyz_min = (x_data[z_min_index], y_data[z_min_index], z_min)

    # z_norm = (z_data - z_min) / (z_max - z_min)


    # Set color limits
    color_z_lims = list( np.linspace(z_min, z_max, len(ccodes)+1) )
    # color_z_norm_lims = list( np.linspace(0.0, 1.0, len(ccodes)+1) )
    # print("DEBUG:", color_z_norm_lims)

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples(x_data, y_data, z_data, xy_bins, x_range, y_range, s_data, s_type)


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
                z_norm = (z_val - z_min) / (z_max - z_min)
                # print("DEBUG: xi, yi, z_val, z_norm : ", xi, yi, z_val, z_norm)

                ccode = get_color_code(z_val, z_norm, color_z_lims, s_type, use_capped_z=use_capped_z)
                marker = get_marker(z_norm, s_type, use_capped_z=use_capped_z)

            # Add point to line
            yi_line += utils.prettify(marker, ccode, bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 13
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, fg_ccode, bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=axes_mod_func, ff=ff)

    # Add blank top line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode, insert_pos=0)


    #
    # Add colorbar, legend, etc
    #

    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(input_str, input_fg_ccode, bg_ccode, bold=True)

    # - colorbar
    cb_entries = []
    cb_entries.append( ("", fg_ccode, "", fg_ccode) )
    for i in range(0, len(color_z_lims)-1):
        cb_entries.append( ("|", fg_ccode, 6*regular_marker.strip(), ccodes[i]) )
    cb_entries.append( ("|", fg_ccode, "", fg_ccode) )

    cb_line, cb_width = utils.generate_legend(cb_entries, legend_mod_func, sep=" ", internal_sep="")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode)
    plot_lines, fig_width = utils.insert_line(cb_line, cb_width, plot_lines, fig_width, fg_ccode, bg_ccode)

    # - numbers below the colorbar
    cb_nums_entries = []
    for i in range(0, len(color_z_lims)):
        txt = ff.format(color_z_lims[i])
        if i % 2 == 0:
            cb_nums_entries.append( ("", fg_ccode, txt, fg_ccode) )
        else:
            cb_nums_entries.append( ("", fg_ccode, " " * len(txt), fg_ccode) )
    cb_nums_line, cb_nums_width = utils.generate_legend(cb_nums_entries, legend_mod_func, sep="", internal_sep="")

    plot_lines, fig_width = utils.insert_line(cb_nums_line, cb_nums_width, plot_lines, fig_width, fg_ccode, bg_ccode)

    # - max/min 
    if s_index == z_index:
        legend_maxmin_entries = []
        if s_type == "max":
            point = ("(" + ff2 + ", " + ff2 + ", " + ff2 + ")").format(xyz_max[0], xyz_max[1], xyz_max[2])
            legend_maxmin_entries.append( (" " + special_marker.strip(), fg_ccode, "max(z) point: (x, y, z) = " + point, fg_ccode) )
        else:
            point = ("(" + ff2 + ", " + ff2 + ", " + ff2 + ")").format(xyz_min[0], xyz_min[1], xyz_min[2])
            legend_maxmin_entries.append( (" " + special_marker.strip(), fg_ccode, "min(z) point: (x, y, z) = " + point, fg_ccode) )
        legend_maxmin, legend_maxmin_width = utils.generate_legend(legend_maxmin_entries, legend_mod_func, sep=" ", internal_sep="  ")

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
    z_label = z_name
    s_label = s_name


    #
    # Add info text
    #

    info_lines = []
    info_left_padding = left_padding + " "
    info_lines.append(info_left_padding)

    info_lines.append(info_left_padding + "x-axis: {}".format(x_label))
    if x_transf_expr != "":
        info_lines.append(info_left_padding + "        - transf.: {}".format(x_transf_expr))
    info_lines.append(info_left_padding + "        - range: [{}, {}]".format(ff2.format(x_range[0]), ff2.format(x_range[1])))

    info_lines.append(info_left_padding + "y-axis: {}".format(y_label))
    if y_transf_expr != "":
        info_lines.append(info_left_padding + "        - transf.: {}".format(y_transf_expr))
    info_lines.append(info_left_padding + "        - range: [{}, {}]".format(ff2.format(y_range[0]), ff2.format(y_range[1])))

    info_lines.append(info_left_padding + "z-axis: {}".format(z_label))
    if z_transf_expr != "":
        info_lines.append(info_left_padding + "        - transf.: {}".format(z_transf_expr))
    info_lines.append(info_left_padding + "        - range: [{}, {}]".format(ff2.format(z_range[0]), ff2.format(z_range[1])))

    info_lines.append(info_left_padding + "  sort: {} [{}]".format(z_label, s_type))
    if s_transf_expr != "":
        info_lines.append(info_left_padding + "        - transf.: {}".format(s_transf_expr))

    if use_capped_z:
        info_lines.append(info_left_padding + "capped: z-axis (color) dataset capped at {}".format(ff2.format(args.cap_z_val)))
    info_lines.append(info_left_padding)

    info_lines_lengths = [len(l) for l in info_lines]
    info_width = max(info_lines_lengths)

    for i,line in enumerate(info_lines):
        info_lines[i] = utils.prettify(line + " "*(info_width - len(line)) + "  ", fg_ccode, bg_ccode, bold=False)


    #
    # Fill in missing background color
    #

    plot_lines, info_lines = utils.fill_missing_bg(plot_lines, fig_width, info_lines, info_width, bg_ccode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    for line in info_lines:
        print(line)

    sys.exit()    
