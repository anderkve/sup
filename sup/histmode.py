import sys
import numpy as np
import h5py
import sup.defaults as defaults
import sup.utils as utils
from collections import OrderedDict


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
    [233, 236, 239, 242, 244, 247, 250, 253, 255, 231],  # for black background
    [232, 235, 238, 240, 243, 246, 248, 251, 253, 255][::-1],  # for white background
]
ccodes_grayscale = cmaps_grayscale[0]

cmaps = [
    [53,56,62,26,31,36,42,47,154,226],      # viridis-ish
    [18,20,27,45,122,155,226,214,202,196],  # jet-ish
]
ccodes = cmaps[0]



def get_color_code(z_val, z_norm, color_z_lims):

    # print("DEBUG: z_val:", z_val, "   z_norm:", z_norm)
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
    global ff
    global ff2

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index

    w_index = args.w_index
    use_weights = bool(w_index is not None)

    normalise_histogram = args.normalise_histogram

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    z_range_user = args.z_range
    user_defined_z_range = bool(z_range_user is not None)

    read_slice = slice(*args.read_slice)

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

    if args.reverse_colormap:
        ccodes = ccodes[::-1]

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

    x_data = np.array(f[x_name])[read_slice]
    y_data = np.array(f[y_name])[read_slice]

    w_name = None
    w_data = np.ones(len(x_data))
    if use_weights:
        w_name = dset_names[w_index]
        w_data = np.array(f[w_name])[read_slice]

    filter_names, filter_datasets = utils.get_filters_hdf5(f, filter_indices, read_slice=read_slice)

    f.close()

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(w_data)
    # data_length = len(x_data)

    if use_filters:
        x_data, y_data, w_data = utils.apply_filters([x_data, y_data, w_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    w_transf_expr = args.w_transf_expr
    z_transf_expr = args.z_transf_expr
    # @todo: add the x,y,w variables to a dictionary of allowed arguments to eval()
    x = x_data
    y = y_data
    w = w_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if w_transf_expr != "":
        w_data = eval(w_transf_expr)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]



    #
    # Get a dict with info per bin
    #

    bins_content_unweighted,_ ,_  = np.histogram2d(x_data, y_data, bins=xy_bins, range=[x_range, y_range], density=normalise_histogram) 
    bins_content, x_bin_limits, y_bin_limits = np.histogram2d(x_data, y_data, bins=xy_bins, range=[x_range, y_range], weights=w_data, density=normalise_histogram) 

    # Apply z-axis transformation to non-empty bins
    z = bins_content[bins_content_unweighted > 0]
    if z_transf_expr != "":
        bins_content[bins_content_unweighted > 0] = eval(z_transf_expr)



    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    bins_info = OrderedDict()
    for i,xi in enumerate(x_bin_centres):
        for j,yj in enumerate(y_bin_centres):

            bin_key = (i,j)
            z_val = bins_content[bin_key]      
            bin_count = bins_content_unweighted[bin_key]

            if bin_count > 0:
                bins_info[bin_key] = (xi, yj, z_val)

    # Get z max and minimum from data if not set by the user
    z_range = None
    if user_defined_z_range:
        z_range = z_range_user
    else:
        z_range = [np.min(bins_content), np.max(bins_content)]
    z_min, z_max = z_range 

    # Set color limits
    color_z_lims = list( np.linspace(z_min, z_max, len(ccodes)+1) )


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
                if z_norm > 1.0:
                    z_norm = 1.0
                elif z_norm < 0.0:
                    z_norm = 0.0

                ccode = get_color_code(z_val, z_norm, color_z_lims)
                marker = get_marker(z_norm)

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
    # Add colorbar, legend, etc
    #

    plot_lines, fig_width = utils.generate_colorbar(plot_lines, fig_width, ff,
                                                    ccodes, color_z_lims, 
                                                    fg_ccode, bg_ccode, empty_bin_ccode)
        

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
    z_label = "bin height"
    w_label = w_name

    #
    # Add info text
    #

    info_lines = utils.generate_info_text(ff2,
                                          x_label, x_range, 
                                          y_label, y_range, 
                                          z_label, z_range, 
                                          x_transf_expr = x_transf_expr, 
                                          y_transf_expr = y_transf_expr,
                                          z_transf_expr = z_transf_expr,
                                          w_label = w_label,
                                          w_transf_expr = w_transf_expr,
                                          filter_names=filter_names,
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
