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

# regular_marker_up = " ▀"
regular_marker_up = " █"
regular_marker_down = " ▄"

# regular_marker = " ●"
# regular_marker = " ▁"
# regular_marker = " ▔"

special_marker = " 🟊"  # " ★" " 🟊" " ✱"

# fill_marker = "  "
# fill_marker = " ■"
fill_marker = " █"

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

ccode_color_bb = 3 # 2  # 231
ccode_color_wb = 11 # 10 # 232
ccode = ccode_color_bb

bar_ccodes_grayscale = [243, 240]
bar_ccodes_color = [4,12]
bar_ccodes = bar_ccodes_color


def get_color_code(z_val):

    if z_val in [1,2]:
        return ccode
    elif z_val == -1:
        return ccode
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

def run(args):

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
    global bar_ccodes
    global empty_bin_marker
    global special_marker
    global ff
    global ff2

    input_file = args.input_file

    x_index = args.x_index

    w_index = args.w_index
    use_weights = bool(w_index is not None)

    normalize_histogram = True

    credible_regions = args.credible_regions
    if not credible_regions:
        credible_regions = [68., 95.]
    # if credible_regions[-1] < 100.:
    # credible_regions.append(100.0)

    credible_regions = np.array(credible_regions)
    if np.any(credible_regions>100.0):
        raise Exception("Can't have a credible region with more than 100% probability.")
    elif np.any(credible_regions<=0.0):
        raise Exception("Can't have a credible region with <= 0% probability.")


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
        bar_ccodes = bar_ccodes_grayscale

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    f = h5py.File(input_file, "r")

    dset_names = utils.get_dataset_names(f)
    x_name = dset_names[x_index]

    x_data = np.array(f[x_name])[read_slice]

    w_name = None
    w_data = np.ones(len(x_data))
    if use_weights:
        w_name = dset_names[w_index]
        w_data = np.array(f[w_name])[read_slice]

    filter_names, filter_datasets = utils.get_filters_hdf5(f, filter_indices, read_slice=read_slice)

    f.close()

    assert len(x_data) == len(w_data)
    # data_length = len(x_data)

    if use_filters:
        x_data, w_data = utils.apply_filters([x_data, w_data], filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    w_transf_expr = args.w_transf_expr

    # @todo: add the x,y,w variables to a dictionary of allowed arguments to eval()
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

    bins_content_unweighted,_  = np.histogram(x_data, bins=xy_bins[0], range=x_range, density=normalize_histogram) 
    bins_content, x_bin_limits = np.histogram(x_data, bins=xy_bins[0], range=x_range, weights=w_data, density=normalize_histogram) 

    # Apply y-axis transformation
    bins_content_not_transformed = bins_content
    y = bins_content
    if y_transf_expr != "":
        bins_content = eval(y_transf_expr)

    dx = x_bin_limits[1] - x_bin_limits[0]
    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx

    if not y_range:
        y_range = [np.min(bins_content[bins_content > -np.inf]), np.max(bins_content)]
    y_min, y_max = y_range

    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg_1d(x_bin_centres, np.minimum(bins_content, y_max), xy_bins, x_range, y_range, fill_below=True, split_marker=True)


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
    # Add horizontal CR region bars
    #

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode)

    cr_bar_lines = utils.generate_credible_region_bars(credible_regions, bins_content_not_transformed, x_bin_limits, ff2)

    for i,line in enumerate(cr_bar_lines):
        cr_bar_width = len(line)
        cr_bar = utils.prettify(line, bar_ccodes[i % 2], bg_ccode)
        plot_lines, fig_width = utils.insert_line(cr_bar, cr_bar_width, plot_lines, fig_width, fg_ccode, bg_ccode)


    #
    # Add legend
    #

    # max bin legend
    legend_mod_func = lambda input_str, input_fg_ccode : utils.prettify(input_str, input_fg_ccode, bg_ccode, bold=True)

    maxbin_index = np.argmax(bins_content)
    maxbin_content = bins_content[maxbin_index]
    maxbin_limits = [x_bin_limits[maxbin_index], x_bin_limits[maxbin_index+1]]
    
    maxbin_str = "max bin:  x: "
    maxbin_str += ("(" + ff2 + ", " + ff2 + ")").format(maxbin_limits[0], maxbin_limits[1])
    maxbin_str += "  bin height: "
    maxbin_str += (ff2).format(maxbin_content)

    legend_maxbin_entries = []
    legend_maxbin_entries.append( ("", fg_ccode, maxbin_str, fg_ccode) )
    legend_maxbin, legend_maxbin_width = utils.generate_legend(legend_maxbin_entries, legend_mod_func, sep="  ", internal_sep=" ")

    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode)
    plot_lines, fig_width = utils.insert_line(legend_maxbin, legend_maxbin_width, plot_lines, fig_width, fg_ccode, bg_ccode)


    #
    # Add left padding
    #

    for i,line in enumerate(plot_lines):
        plot_lines[i] = utils.prettify(left_padding, fg_ccode, bg_ccode) + line


    #
    # Set labels
    #

    x_label = x_name
    y_label = "bin height"
    w_label = w_name


    #
    # Add info text
    #

    info_lines = utils.generate_info_text(ff2,
                                          x_label, x_range, 
                                          x_bin_width=dx,
                                          y_label=y_label, y_range=y_range, 
                                          x_transf_expr=x_transf_expr, 
                                          y_transf_expr=y_transf_expr,
                                          y_normalized_hist=normalize_histogram,
                                          w_label=w_label,
                                          w_transf_expr=w_transf_expr,
                                          filter_names=filter_names,
                                          mode_name="posterior",
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
