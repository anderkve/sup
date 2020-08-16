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
empty_bin_marker_color = " □"
empty_bin_marker = empty_bin_marker_color

empty_bin_ccode_grayscale_bb = 237
empty_bin_ccode_grayscale_wb = 252
empty_bin_ccode_grayscale = empty_bin_ccode_grayscale_bb

empty_bin_ccode_color_bb = 237
empty_bin_ccode_color_wb = 252
empty_bin_ccode = empty_bin_ccode_color_bb

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



def get_color_code(z_val, z_norm, color_z_lims):

    if z_norm == 1.0:
        return ccodes[-1]
    elif z_norm == 0.0:
        return ccodes[0]

    i = 0
    for j, lim in enumerate(color_z_lims):
        if z_val >= lim:
            i = j
        else:
            break
    return ccodes[i]


def get_marker(z_norm):

    return regular_marker


#
# Run
#

def run(args):

    assert args.cmap_index in range(len(cmaps))

    global ccodes 
    global ccodes_grayscale 
    global bg_ccode
    global fg_ccode
    global empty_bin_ccode
    global empty_bin_ccode_grayscale
    global empty_bin_marker
    global special_marker
    global color_z_lims

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index
    z_index = args.z_index

    x_range = args.x_range
    y_range = args.y_range

    read_length = defaults.read_length

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins
    
    cmap_index = args.cmap_index
    ccodes = cmaps[cmap_index]
    use_white_bg = args.use_white_bg
    if use_white_bg:
        bg_ccode = bg_ccode_wb
        fg_ccode = fg_ccode_wb
        empty_bin_ccode = empty_bin_ccode_color_wb
        # ccodes = ccodes_color_wb

    if args.use_grayscale:
        if use_white_bg:
            ccodes = cmaps_grayscale[1]
            # ccodes = ccodes_grayscale_wb
            empty_bin_ccode = empty_bin_ccode_grayscale_wb
        else:
            ccodes = cmaps_grayscale[0]
            # ccodes = ccodes_grayscale_bb
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

    x_data = np.array(f[x_name])[:read_length]
    y_data = np.array(f[y_name])[:read_length]
    z_data = np.array(f[z_name])[:read_length]

    f.close()

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(z_data)
    # data_length = len(x_data)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    z_transf_expr = args.z_transf_expr
    x = x_data
    y = y_data
    z = z_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if z_transf_expr != "":
        z_data = eval(z_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]

    # Get z max and minimum
    z_min = np.min(z_data)
    z_max = np.max(z_data)
    z_range = [z_min, z_max]

    # z_norm = (z_data - z_min) / (z_max - z_min)

    # Set color limits
    color_z_lims = list( np.linspace(z_min, z_max, len(ccodes)+1) )

    #
    # Get a dict with info per bin
    #

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg(x_data, y_data, z_data, xy_bins, x_range, y_range)


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
                z_norm = 0.0
                if (z_max != z_min):
                    z_norm = (z_val - z_min) / (z_max - z_min)

                ccode = get_color_code(z_val, z_norm, color_z_lims)
                marker = get_marker(z_norm)

            # Add point to line
            yi_line += utils.prettify(marker, ccode, bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    # Save plot width
    plot_width = xy_bins[0] * 2 + 13
    fig_width = plot_width

    # Add axes
    axes_mod_func = lambda input_str : utils.prettify(input_str, fg_ccode, bg_ccode, bold=True)
    plot_lines = utils.add_axes(plot_lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=axes_mod_func, floatf=ff)

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
    z_label = z_name + " [binned average]"


    #
    # Add info text
    #

    info_lines = utils.generate_info_text(x_label, x_range, 
                                          y_label, y_range, 
                                          z_label, z_range, 
                                          x_transf_expr = x_transf_expr, 
                                          y_transf_expr = y_transf_expr,
                                          z_transf_expr = z_transf_expr, 
                                          left_padding = left_padding + " ")

    for i,line in enumerate(info_lines):
        pretty_line = utils.prettify(line + "  ", fg_ccode, bg_ccode, bold=False)
        plot_lines, fig_width = utils.insert_line(pretty_line, len(line), plot_lines, fig_width, fg_ccode, bg_ccode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    sys.exit()    
