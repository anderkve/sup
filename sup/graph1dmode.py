import sys
import numpy as np
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

ccode_color_bb = 4  # 231
ccode_color_wb = 12 # 232
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
    global empty_bin_marker
    global special_marker
    global ff
    global ff2

    function_str = args.function

    x_range = args.x_range
    y_range = args.y_range

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
    # Generate datasets from function defintion
    #

    # Generate x dataset based on x range and number of bins
    if not x_range:
        x_range = [0.0, 1.0]

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range

    # Get index of max-z point in each bin
    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx

    x_data = x_bin_centres

    y_data = np.zeros(shape=x_data.shape)

    # Need this declaration such the 'x' can be used in the eval input string
    x = x_data

    # Create y data set by evaluating the function_str
    y_data = eval(function_str)

    assert len(x_data) == len(y_data)

    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]


    #
    # Get a dict with info per bin
    #

    # @todo Don't use the 'avg' version for this.
    bins_info, x_bin_limits, y_bin_limits = utils.get_bin_tuples_avg_1d(x_data, y_data, xy_bins, x_range, y_range, fill_below=False, split_marker=True)


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
    # Add left padding
    #

    for i,line in enumerate(plot_lines):
        plot_lines[i] = utils.prettify(left_padding, fg_ccode, bg_ccode) + line


    #
    # Set labels
    #

    x_label = "x"
    y_label = "f(x) = " + function_str


    #
    # Add info text
    #

    info_lines = utils.generate_info_text(ff2,
                                          x_label, x_range, 
                                          y_label=y_label, y_range=y_range, 
                                          mode_name="graph",
                                          left_padding=left_padding + " ")

    for i,line in enumerate(info_lines):
        pretty_line = utils.prettify(line + "  ", fg_ccode, bg_ccode, bold=False)
        plot_lines, fig_width = utils.insert_line(pretty_line, len(line), plot_lines, fig_width, fg_ccode, bg_ccode)


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
