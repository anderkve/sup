import sys
import numpy as np
import h5py
import sup.defaults
from sup.utils import get_bin_tuples, get_dataset_names, add_axes, prettify
import shutil

# from sup.colors import ccodes, n_colors

# color_codes = [236,19,27,45,87,122,155,190,226]
# color_z_lims = []


#
# Variables for colors, markers and padding
#

left_padding = 2*" "

ccode_bg = 232
ccode_fg = 255

regular_marker = " ■"
special_marker = " 🟊"  # " ★" " 🟊" " ✱"

empty_bin_marker_grayscale = " □"
empty_bin_marker_color = " ■"
empty_bin_marker = empty_bin_marker_color

empty_bin_ccode_grayscale = 233
empty_bin_ccode_color = 233
empty_bin_ccode = empty_bin_ccode_color

max_bin_ccode_grayscale = 255
max_bin_ccode_color = 255
max_bin_ccode = max_bin_ccode_color

# 232 --> 255
ccodes_grayscale = [233, 235, 242, 255]
ccodes_color = [236, 19, 45, 226]
ccodes = ccodes_color

color_z_lims = [0.0, 0.003, 0.046, 0.317]

def get_color_code(z_norm, use_grayscale=False):

    if z_norm == 1.0:
        return max_bin_ccode

    i = 0
    for j, lim in enumerate(color_z_lims):
        if z_norm > lim:
            i = j
        else:
            break
    return ccodes[i]


def get_marker(z_norm):

    if z_norm == 1.0:
        return special_marker
    else:
        return regular_marker


#
# Run
#

def run(args):

    term_cols, term_lines = shutil.get_terminal_size()

    global ccodes 
    global max_bin_ccode
    global empty_bin_ccode
    global empty_bin_marker
    global special_marker

    input_file = args.input_file
    x_index = args.x_index
    y_index = args.y_index
    loglike_index = args.loglike_index
    s_index = args.loglike_index
    s_type = "max"

    x_range = args.x_range
    y_range = args.y_range

    z_min = sup.defaults.z_min
    z_max = sup.defaults.z_max

    read_length = sup.defaults.read_length

    x_use_abs_val = args.x_use_abs_val
    y_use_abs_val = args.y_use_abs_val
    # z_use_abs_val = sup.defaults.z_use_abs_val
    s_use_abs_val = False

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = sup.defaults.xy_bins
    
    # even_x_bins = False
    # if xy_bins[0] % 2 == 0:
    #     even_x_bins = True
    # even_y_bins = False
    # if xy_bins[1] % 2 == 0:
    #     even_y_bins = True

    if args.use_grayscale:
        ccodes = ccodes_grayscale
        max_bin_ccode = max_bin_ccode_grayscale
        empty_bin_ccode = empty_bin_ccode_grayscale
        empty_bin_marker = empty_bin_marker_grayscale

    use_capped_loglike = False
    if args.cap_loglike_val is not None:
        use_capped_loglike = True
        special_marker = regular_marker


    #
    # Read datasets from file
    #

    f = h5py.File(input_file, "r")

    dset_names = get_dataset_names(f)
    x_name = dset_names[x_index]
    y_name = dset_names[y_index]
    loglike_name = dset_names[loglike_index]
    s_name = dset_names[s_index]

    x_data = np.array(f[x_name])[:read_length]
    y_data = np.array(f[y_name])[:read_length]
    loglike_data = np.array(f[loglike_name])[:read_length]
    s_data = np.array(f[s_name])[:read_length]

    f.close()

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(loglike_data)
    assert len(x_data) == len(s_data)
    # data_length = len(x_data)


    if x_use_abs_val:
        x_data = np.abs(x_data)
    if y_use_abs_val:
        y_data = np.abs(y_data)
    if s_use_abs_val:
        s_data = np.abs(s_data)

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
        loglike_data = np.minimum(loglike_data, 0.)


    #
    # Create likelihood ratio dataset
    #

    loglike_max = np.max(loglike_data)
    likelihood_ratio = np.exp(loglike_data) / np.exp(loglike_max)


    #
    # Get a dict with info per bin
    #

    z_data = likelihood_ratio
    s_data = z_data  # sort according to likelihood_ratio
    if not z_min:
        z_min = np.min(z_data)
    if not z_max:
        z_max = np.max(z_data)

    bins_info, x_bin_limits, y_bin_limits = get_bin_tuples(x_data, y_data, z_data, xy_bins, x_range, y_range, s_data, s_type)

    # # DEBUG:
    # for k in bins_info.keys():
    #     print(bins_info[k])


    #
    # Generate string to be printed
    #

    lines = []
    for yi in range(xy_bins[1]):

        yi_line = ""

        for xi in range(xy_bins[0]):

            xiyi = (xi,yi)

            ccode = empty_bin_ccode
            marker = empty_bin_marker

            if xiyi in bins_info.keys():
                z_val = bins_info[xiyi][2]
                z_norm = z_val
                # z_norm = (z_val - z_min) / (z_max - z_min)

                ccode = get_color_code(z_norm)
                marker = get_marker(z_norm)

            # Add point to line
            yi_line += prettify(marker, ccode, ccode_bg)

        lines.append(yi_line)

    lines.reverse()


    # Add axes
    axes_mod_func = lambda input_str : prettify(input_str, ccode_fg, ccode_bg, bold=True)
    lines = add_axes(lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=axes_mod_func)

    # Add legend
    plot_width = xy_bins[0] * 2 + 12

    legend = ""
    legend_length = 0
    if not use_capped_loglike:
        legend += prettify(special_marker.strip(), max_bin_ccode, ccode_bg) + prettify(" best-fit", ccode_fg, ccode_bg)
        legend += prettify("  ", ccode_fg, ccode_bg)
        legend_length += len("* best-fit  ")

    legend += prettify(regular_marker.strip(), ccodes[-1], ccode_bg) + prettify(" 1σ", ccode_fg, ccode_bg)
    legend += prettify("  ", ccode_fg, ccode_bg)
    legend_length += len("* 1σ  ")
    legend += prettify(regular_marker.strip(), ccodes[-2], ccode_bg) + prettify(" 2σ", ccode_fg, ccode_bg)
    legend += prettify("  ", ccode_fg, ccode_bg)
    legend_length += len("* 2σ  ")
    legend += prettify(regular_marker.strip(), ccodes[-3], ccode_bg) + prettify(" 3σ", ccode_fg, ccode_bg)
    legend += prettify("  ", ccode_fg, ccode_bg)
    legend_length += len("* 3σ  ")

    legend += prettify(" " * (plot_width - legend_length), ccode_fg, ccode_bg)

    lines.append(prettify(" " * plot_width, ccode_fg, ccode_bg) )
    lines.append(legend)
    # lines.append(prettify(" " * plot_width, ccode_fg, ccode_bg) )

    # Add top line
    lines = [prettify(" " * plot_width, ccode_fg, ccode_bg)] + lines

    #
    # Set labels
    #

    x_label = x_name
    y_label = y_name
    z_label = "likelihood ratio (L/L_max)"
    s_label = z_label


    #
    # Add padding for plot
    #

    for i,line in enumerate(lines):
        lines[i] = prettify(left_padding, ccode_fg, ccode_bg) + line

    #
    # Add info text
    #

    info_lines = []
    info_lines.append(left_padding)
    info_lines.append(left_padding + "x-axis : {n} {mm}".format(n=x_label, mm=x_range))
    info_lines.append(left_padding + "y-axis : {n} {mm}".format(n=y_label, mm=y_range))
    info_lines.append(left_padding + " color : {n}".format(n=z_label))
    info_lines.append(left_padding + "  sort : {n} [{t}]".format(n=s_label, t=s_type))
    if use_capped_loglike:
        info_lines.append(left_padding + "capped : ln(L) dataset ({n}) capped at {v}".format(n=loglike_name, v=args.cap_loglike_val))
    info_lines.append(left_padding)

    info_lines_lengths = [len(l) for l in info_lines]
    info_lines_width = max(info_lines_lengths)

    for i,line in enumerate(info_lines):
        info_lines[i] = prettify(line + " "*(info_lines_width - len(line)) + "  ", ccode_fg, ccode_bg)


    #
    # Fill in missing background color
    #

    width_diff = info_lines_width - plot_width
    if width_diff > 0:
        for i,line in enumerate(lines):
            lines[i] += prettify(" " * width_diff, ccode_fg, ccode_bg)
    elif width_diff < 0:
        for i,line in enumerate(info_lines):
            info_lines[i] += prettify(" " * int(abs(width_diff)), ccode_fg, ccode_bg)


    #
    # Print everything
    #

    for line in lines:
        print(line)

    for info_line in info_lines:
        print(info_line)

    sys.exit()    
