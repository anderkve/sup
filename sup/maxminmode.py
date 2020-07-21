import sys
import numpy as np
import h5py
import sup.defaults
from sup.utils import get_bin_tuples, get_dataset_names, add_axes, prettify, fill_missing_bg, generate_legend


#
# Variables for colors, markers, padding, etc
#

ff = sup.defaults.ff
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

empty_bin_ccode_grayscale_bb = 233
empty_bin_ccode_grayscale_wb = 254
empty_bin_ccode_grayscale = empty_bin_ccode_grayscale_bb

empty_bin_ccode_color_bb = 237
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

ccodes_color_bb = [18,20,27,45,122,155,226,214,202,196]
ccodes_color_wb = [18,20,27,45,122,155,226,214,202,196]
ccodes = ccodes_color_bb

# color_z_lims = [0.0, 0.25, 0.50, 0.75]


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

    # z_min = sup.defaults.z_min
    # z_max = sup.defaults.z_max

    read_length = sup.defaults.read_length

    x_use_abs_val = args.x_use_abs_val
    y_use_abs_val = args.y_use_abs_val
    z_use_abs_val = args.z_use_abs_val
    s_use_abs_val = args.s_use_abs_val
    if s_index == z_index:
        s_use_abs_val = z_use_abs_val

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = sup.defaults.xy_bins
    
    use_capped_z = False
    if args.cap_z_val is not None:
        use_capped_z = True

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

    n_colors = args.n_colors
    if n_colors < 1:
        n_colors = 1
    elif n_colors > 10:
        n_colors = 10
    ccodes = ccodes[:n_colors]

    #
    # Read datasets from file
    #

    f = h5py.File(input_file, "r")

    dset_names = get_dataset_names(f)
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


    if x_use_abs_val:
        x_data = np.abs(x_data)
    if y_use_abs_val:
        y_data = np.abs(y_data)
    if z_use_abs_val:
        z_data = np.abs(z_data)
    if s_use_abs_val:
        s_data = np.abs(s_data)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]

    # Cap z dataset?
    if use_capped_z:
        z_data = np.minimum(z_data, args.cap_z_val)

    # Get z max and minimum
    z_min = np.min(z_data)
    z_max = np.max(z_data)
    z_range = [z_min, z_max]
    # z_norm = (z_data - z_min) / (z_max - z_min)


    # Set color limits
    color_z_lims = list( np.linspace(z_min, z_max, len(ccodes)+1) )
    # color_z_norm_lims = list( np.linspace(0.0, 1.0, len(ccodes)+1) )
    # print("DEBUG:", color_z_norm_lims)

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = get_bin_tuples(x_data, y_data, z_data, xy_bins, x_range, y_range, s_data, s_type)


    #
    # Generate string to be printed
    #

    plot_lines = []
    for yi in range(xy_bins[1]):

        yi_line = ""

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
            yi_line += prettify(marker, ccode, bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()


    # Add axes
    axes_mod_func = lambda input_str : prettify(input_str, fg_ccode, bg_ccode, bold=True)
    plot_lines = add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=axes_mod_func, ff=ff)

    # Add top line
    plot_width = xy_bins[0] * 2 + 12
    plot_lines = [prettify(" " * plot_width, fg_ccode, bg_ccode)] + plot_lines

    # Add legend
    legend_mod_func = lambda input_str, input_fg_ccode : prettify(input_str, input_fg_ccode, bg_ccode, bold=True)
    legend_entries = []

    # legend_entries.append( ("  " + special_marker.strip() + "       ", max_bin_ccode, "", fg_ccode) )
    # for i in range(len(color_z_lims[:-1])-1, -1, -1):
    #     legend_entries.append( (5*regular_marker.strip(), ccodes[i], "", fg_ccode) )
    # legend, legend_width = generate_legend(legend_entries, legend_mod_func, sep=" ")
    # legend += prettify(" " * (plot_width - legend_width), fg_ccode, bg_ccode)

    # legend_entries.append( ("  " + special_marker.strip() + "       ", max_bin_ccode, "", fg_ccode) )
    for i in range(len(color_z_lims[:-1])-1, -1, -1):
        legend_entries.append( ("|", fg_ccode, 7*regular_marker.strip(), ccodes[i]) )
    legend_entries.append( ("|", fg_ccode, "", fg_ccode) )
    legend, legend_width = generate_legend(legend_entries, legend_mod_func, sep=" ", internal_sep="")
    legend += prettify(" " * (plot_width - legend_width), fg_ccode, bg_ccode)

    # Add a blank line and then the legend
    plot_lines.append(prettify(" " * plot_width, fg_ccode, bg_ccode) )
    plot_lines.append(legend)

    # # Vertical ticks down from colorbar limits
    # legend_entries = []
    # legend_entries.append( ("  │      ", fg_ccode, "", fg_ccode) )
    # for i in range(len(color_z_lims[:-1])-1, -1, -1):
    #     legend_entries.append( (" │    ", fg_ccode, "", fg_ccode) )
    # legend_entries.append( (" │    ", fg_ccode, "", fg_ccode) )
    # legend, legend_width = generate_legend(legend_entries, legend_mod_func, sep="")
    # legend += prettify(" " * (plot_width - legend_width), fg_ccode, bg_ccode)
    # plot_lines.append(legend)

    # Numbers below the colorbar ticks
    legend_entries = []
    for i in range(len(color_z_lims)-1, -1, -1):
        legend_entries.append( ("", fg_ccode, ff.format(color_z_lims[i]), fg_ccode) )
    legend, legend_width = generate_legend(legend_entries, legend_mod_func, sep="  ", internal_sep="")
    legend += prettify(" " * (plot_width - legend_width), fg_ccode, bg_ccode)
    plot_lines.append(legend)


    # Add left padding
    for i,line in enumerate(plot_lines):
        plot_lines[i] = prettify(left_padding, fg_ccode, bg_ccode) + line


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
    info_lines.append(left_padding)
    info_lines.append(left_padding + "x-axis : {} [{}, {}]".format(x_label, ff.format(x_range[0]), ff.format(x_range[1])))
    info_lines.append(left_padding + "y-axis : {} [{}, {}]".format(y_label, ff.format(y_range[0]), ff.format(y_range[1])))
    info_lines.append(left_padding + " color : {} [{}, {}]".format(z_label, ff.format(z_range[0]), ff.format(z_range[1])))
    info_lines.append(left_padding + "  sort : {} [{}]".format(s_label, s_type))
    if use_capped_z:
        info_lines.append(left_padding + "capped : z-axis (color) dataset capped at {}".format(ff.format(args.cap_z_val)))
    info_lines.append(left_padding)

    info_lines_lengths = [len(l) for l in info_lines]
    info_width = max(info_lines_lengths)

    for i,line in enumerate(info_lines):
        info_lines[i] = prettify(line + " "*(info_width - len(line)) + "  ", fg_ccode, bg_ccode, bold=False)


    #
    # Fill in missing background color
    #

    plot_lines, info_lines = fill_missing_bg(plot_lines, plot_width, info_lines, info_width, bg_ccode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    for line in info_lines:
        print(line)

    sys.exit()    
