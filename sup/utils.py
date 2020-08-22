import numpy as np
from collections import OrderedDict
import h5py


def prettify(input_string, fg_ccode, bg_ccode, bold=True, reset=True):
    # example: "\u001b[48;5;" + str(bg_ccode) + ";38;5;" + str(fg_ccode) + "m" + input_string + "\u001b[0m"
    result = "\u001b" 
    result += "[" 
    result += "48;5;" +str(bg_ccode) + ";"
    if bold:
        result += "1;"
    result += "38;5;" + str(fg_ccode) + "m"
    result += input_string 
    if reset:
        result += "\u001b[0m"

    return result


def insert_line(new_line, new_line_width, old_lines_list, old_width, fg_ccode, bg_ccode, insert_pos=None):

    # If no insert position is given, append the line to the end of the list
    if insert_pos is None:
        insert_pos = len(old_lines_list)

    result_width = 0
    result_lines_list = old_lines_list

    if new_line_width <= old_width:
        new_line += prettify(" " * (old_width - new_line_width), fg_ccode, bg_ccode)
        result_width = old_width
    else:
        for i in range(len(result_lines_list)):
            result_lines_list[i] += prettify(" " * (new_line_width - old_width), fg_ccode, bg_ccode)
        result_width = new_line_width

    result_lines_list.insert(insert_pos, new_line)

    return result_lines_list, result_width


def fill_missing_bg(lines_1, width_1, lines_2, width_2, bg_ccode):
    width_diff = width_1 - width_2
    if width_diff > 0:
        for i,line in enumerate(lines_2):
            lines_2[i] += prettify(" " * width_diff, bg_ccode, bg_ccode)
    elif width_diff < 0:
        for i,line in enumerate(lines_1):
            lines_1[i] += prettify(" " * int(abs(width_diff)), bg_ccode, bg_ccode)
    return lines_1, lines_2


def generate_legend(legend_entries, mod_func, sep="  ", internal_sep=" "):

    legend = ""
    legend_width = 0

    for entry_tuple in legend_entries:
        marker, marker_ccode, txt, txt_ccode = entry_tuple
        legend += mod_func(marker, marker_ccode) + mod_func(internal_sep + txt, txt_ccode)
        legend += mod_func(sep, txt_ccode)
        legend_width += len(marker) + len(internal_sep) + len(txt) + len(sep)

    return legend, legend_width


def generate_colorbar(plot_lines, fig_width, ff,
                      ccodes, color_z_lims,
                      fg_ccode, bg_ccode, empty_bin_ccode):

    legend_mod_func = lambda input_str, input_fg_ccode : prettify(input_str, input_fg_ccode, bg_ccode, bold=True)

    # - colorbar
    cb_entries = []
    cb_entries.append( ("", fg_ccode, "", fg_ccode) )
    n_color_lims = len(color_z_lims)
    for i in range(0, n_color_lims):
        bar_ccode = fg_ccode
        if i % 2 == 1:
            bar_ccode = empty_bin_ccode

        if i < (n_color_lims - 1):
            cb_entries.append( ("|", bar_ccode, 6*"■", ccodes[i]) )
        else:
            cb_entries.append( ("|", bar_ccode, "", fg_ccode) )

    cb_line, cb_width = generate_legend(cb_entries, legend_mod_func, sep=" ", internal_sep="")

    plot_lines, fig_width = insert_line("", 0, plot_lines, fig_width, fg_ccode, bg_ccode)
    plot_lines, fig_width = insert_line(cb_line, cb_width, plot_lines, fig_width, fg_ccode, bg_ccode)

    # - numbers below the colorbar
    cb_nums_entries = []
    for i in range(0, n_color_lims):
        txt = ff.format(color_z_lims[i])
        if i % 2 == 0:
            cb_nums_entries.append( ("", fg_ccode, txt, fg_ccode) )
        else:
            gap_length = 8
            if len(txt) > gap_length:
                gap_length = gap_length - (len(txt) - gap_length) 
            cb_nums_entries.append( ("", fg_ccode, " " * gap_length, fg_ccode) )

    cb_nums_line, cb_nums_width = generate_legend(cb_nums_entries, legend_mod_func, sep="", internal_sep="")

    plot_lines, fig_width = insert_line(cb_nums_line, cb_nums_width, plot_lines, fig_width, fg_ccode, bg_ccode)

    return plot_lines, fig_width


def generate_info_text(ff2, x_label, x_range, y_label, y_range, z_label, z_range, 
                       x_transf_expr="", y_transf_expr="", z_transf_expr="", 
                       s_label=None, s_type=None, s_transf_expr="", 
                       w_label=None, w_transf_expr="",
                       capped_z=False, capped_label="z-axis", cap_val=1e99,
                       filter_names=[],
                       left_padding=""):

    info_lines = []
    info_lines.append(left_padding)

    info_lines.append(left_padding + "x-axis: {}".format(x_label))
    if x_transf_expr != "":
        info_lines.append(left_padding + "  - transf.: {}".format(x_transf_expr))
    info_lines.append(left_padding + "  - range: [{}, {}]".format(ff2.format(x_range[0]), ff2.format(x_range[1])))

    info_lines.append(left_padding + "y-axis: {}".format(y_label))
    if y_transf_expr != "":
        info_lines.append(left_padding + "  - transf.: {}".format(y_transf_expr))
    info_lines.append(left_padding + "  - range: [{}, {}]".format(ff2.format(y_range[0]), ff2.format(y_range[1])))

    info_lines.append(left_padding + "z-axis: {}".format(z_label))
    if z_transf_expr != "":
        info_lines.append(left_padding + "  - transf.: {}".format(z_transf_expr))
    info_lines.append(left_padding + "  - range: [{}, {}]".format(ff2.format(z_range[0]), ff2.format(z_range[1])))

    if (s_label is not None) and (s_type is not None):
        info_lines.append(left_padding + "sort: {} [{}]".format(s_label, s_type))
        if s_transf_expr != "":
            info_lines.append(left_padding + "  - transf.: {}".format(s_transf_expr))

    if w_label is not None:
        info_lines.append(left_padding + "weights: {}".format(w_label))
        if w_transf_expr != "":
            info_lines.append(left_padding + "  - transf.: {}".format(w_transf_expr))

    if capped_z:
        info_lines.append(left_padding + "capped: {} dataset capped at {}".format(capped_label, ff2.format(cap_val)))

    for f_name in filter_names:
        info_lines.append(left_padding + "filter: {}".format(f_name))

    info_lines.append(left_padding)

    return info_lines


def get_dataset_names(hdf5_file_object):
    result = []
    def get_datasets(name, obj):
        if type(obj) is h5py._hl.dataset.Dataset:
            result.append(name)

    hdf5_file_object.visititems(get_datasets)
    return result


def get_bin_tuples_maxmin(x_data, y_data, z_data, xy_bins, x_range, y_range, s_data, s_type):

    assert s_type in ["min", "max"]
    assert len(x_data) == len(y_data)
    assert len(x_data) == len(z_data)
    data_length = len(x_data)

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range
    y_min, y_max = y_range

    # Get index of max-z point in each bin
    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)
    y_bin_limits = np.linspace(y_min, y_max, y_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    xdata_xbin_numbers = np.digitize(x_data, x_bin_limits) - 1
    ydata_ybin_numbers = np.digitize(y_data, y_bin_limits) - 1

    # Prepare dictionary: (x_bin_index, y_bin_index) --> [(z_val, data_index), (z_val, data_index), ...]
    bins_dict = OrderedDict()
    for x_bin_number in range(x_bins):
        for y_bin_number in range(y_bins):
            bin_key = (x_bin_number, y_bin_number)
            bins_dict[bin_key] = {}
            bins_dict[bin_key]["x_centre"] = x_bin_centres[x_bin_number]
            bins_dict[bin_key]["y_centre"] = y_bin_centres[y_bin_number]
            bins_dict[bin_key]["z_vals"] = []
            bins_dict[bin_key]["s_vals"] = []
            bins_dict[bin_key]["data_indices"] = []
            # bins_dict[bin_key]["max_z_val"] = -1
            # bins_dict[bin_key]["max_z_data_index"] = -1

    # Fill the arrays "z_vals" and "data_indices" for each bin
    for di in range(data_length):

        # if di % 1000 == 0:
        #     print("Point", di)

        # x_val = x_data[di]
        # y_val = y_data[di]
        z_val = z_data[di]
        s_val = s_data[di]

        x_bin_number = xdata_xbin_numbers[di]
        y_bin_number = ydata_ybin_numbers[di]

        bin_key = (x_bin_number, y_bin_number)

        if bin_key in bins_dict.keys():

            bins_dict[bin_key]["z_vals"].append(z_val)
            bins_dict[bin_key]["s_vals"].append(s_val)
            bins_dict[bin_key]["data_indices"].append(di)

    # Convert to numpy arrays
    for bin_key in bins_dict.keys():
        bins_dict[bin_key]["z_vals"] = np.array(bins_dict[bin_key]["z_vals"])
        bins_dict[bin_key]["s_vals"] = np.array(bins_dict[bin_key]["s_vals"])
        bins_dict[bin_key]["data_indices"] = np.array(bins_dict[bin_key]["data_indices"])

    # For each bin, sort the arrays according to s_data dataset
    result_dict = OrderedDict()
    for bin_key in bins_dict.keys():

        # Get data index of the z-value for this bin, based on s_data sorting
        ordering = None
        ordering_low_to_high = np.argsort( bins_dict[bin_key]["s_vals"] )
        if s_type == "max":
            ordering = ordering_low_to_high[::-1]
        elif s_type == "min":
            ordering = ordering_low_to_high

        bins_dict[bin_key]["z_vals"] = bins_dict[bin_key]["z_vals"][ordering]
        bins_dict[bin_key]["data_indices"] = bins_dict[bin_key]["data_indices"][ordering]

        if len(bins_dict[bin_key]["z_vals"]) > 0:

            result_dict[bin_key] = (x_bin_centres[bin_key[0]], 
                                    y_bin_centres[bin_key[1]], 
                                    bins_dict[bin_key]["z_vals"][0], 
                                    bins_dict[bin_key]["data_indices"][0])

    return result_dict, x_bin_limits, y_bin_limits


def get_bin_tuples_avg(x_data, y_data, z_data, xy_bins, x_range, y_range):

    assert len(x_data) == len(y_data)
    assert len(x_data) == len(z_data)
    data_length = len(x_data)

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range
    y_min, y_max = y_range

    # Get index of max-z point in each bin
    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)
    y_bin_limits = np.linspace(y_min, y_max, y_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    xdata_xbin_numbers = np.digitize(x_data, x_bin_limits) - 1
    ydata_ybin_numbers = np.digitize(y_data, y_bin_limits) - 1

    # Prepare dictionary: (x_bin_index, y_bin_index) --> [(z_val, data_index), (z_val, data_index), ...]
    bins_dict = OrderedDict()
    for x_bin_number in range(x_bins):
        for y_bin_number in range(y_bins):
            bin_key = (x_bin_number, y_bin_number)
            bins_dict[bin_key] = {}
            bins_dict[bin_key]["x_centre"] = x_bin_centres[x_bin_number]
            bins_dict[bin_key]["y_centre"] = y_bin_centres[y_bin_number]
            bins_dict[bin_key]["z_vals"] = []

    # Fill the arrays "z_vals" and "data_indices" for each bin
    for di in range(data_length):

        z_val = z_data[di]

        x_bin_number = xdata_xbin_numbers[di]
        y_bin_number = ydata_ybin_numbers[di]

        bin_key = (x_bin_number, y_bin_number)

        if bin_key in bins_dict.keys():

            bins_dict[bin_key]["z_vals"].append(z_val)


    # Convert to numpy arrays
    for bin_key in bins_dict.keys():
        bins_dict[bin_key]["z_vals"] = np.array(bins_dict[bin_key]["z_vals"])


    # For each bin, take the average z value
    result_dict = OrderedDict()
    for bin_key in bins_dict.keys():


        if len(bins_dict[bin_key]["z_vals"]) > 0:

            avg_z_val = np.average(bins_dict[bin_key]["z_vals"])

            result_dict[bin_key] = (x_bin_centres[bin_key[0]], 
                                    y_bin_centres[bin_key[1]], 
                                    avg_z_val)

    return result_dict, x_bin_limits, y_bin_limits


def add_axes(lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=None, floatf="{: .1e}"):

    if mod_func is None:
        mod_func = lambda x : x

    even_x_bins = False
    if xy_bins[0] % 2 == 0:
        even_x_bins = True
    even_y_bins = False
    if xy_bins[1] % 2 == 0:
        even_y_bins = True

    mid_x_index = int( np.floor( 0.5 * xy_bins[0] ) )
    mid_y_index = int( np.floor( 0.5 * xy_bins[1] ) )

    x_tick_indicies = []
    tick_spacing = 0
    tick_width = len( "{}".format(floatf.format(0.0)))
    for n_ticks in range(2,10):
        new_indicies = [ int(i) for i in np.floor( np.linspace(0, xy_bins[0], n_ticks) ) ]
        tick_spacing = (new_indicies[1] - new_indicies[0]) * 2
        print("DEBUG: tick_spacing:", tick_spacing, "    tick_width:", tick_width)
        if tick_spacing < tick_width + 1:
            print("DEBUG: BREAK!")
            break
        x_tick_indicies = new_indicies
    n_x_ticks = len(x_tick_indicies)

    print("DEBUG: x_tick_indicies: ", x_tick_indicies)


    #
    # Add axis lines
    #

    # y axis:
    for i in range(xy_bins[1]):
        lines[i] += mod_func(" │")
    lines[mid_y_index - 1*even_y_bins] = lines[mid_y_index - 1*even_y_bins][:-5] + mod_func("│\u0332")
    lines[xy_bins[1]-1] = lines[xy_bins[1]-1][:-5] + mod_func("│\u0332")
    top_line = mod_func(" " + "  " * xy_bins[0] + " _")
    lines = [top_line] + lines

    # x axis:
    x_axis = " "
    for i in range(n_x_ticks):
        if i == 0:
            x_axis += "├─"
        elif i == (n_x_ticks-1):
            x_axis += "┤"
            break
        else:
            x_axis += "┼"
        bin_diff = x_tick_indicies[i+1] - x_tick_indicies[i]
        x_axis += "─" * (bin_diff * 2 - 1)
    x_axis = mod_func(x_axis)
    lines.append(x_axis)

    # x_axis = " ├─"
    # x_axis += "─" * (xy_bins[0] - 1 - 1*(not even_x_bins)) 
    # x_axis += "┼" 
    # x_axis += "─" * (xy_bins[0] - 1 - 1*even_x_bins) 
    # x_axis += "─┤"
    # x_axis = mod_func(x_axis)
    # lines.append(x_axis)

    #
    # Add x and y ticks
    #

    # y ticks
    y_tick_1 = "{}".format(floatf.format(y_bin_limits[0]))
    y_tick_2 = "{}".format(floatf.format(y_bin_limits[mid_y_index]))
    y_tick_3 = "{}".format(floatf.format(y_bin_limits[-1]))

    lines[0] += mod_func("" + y_tick_3 + "  ")
    lines[mid_y_index + 1*(not even_y_bins)] += mod_func("" + y_tick_2 + "  ")
    lines[-2] += mod_func("" + y_tick_1 + "  ")

    for i,line in enumerate(lines):
        if i in [0, mid_y_index + 1*(not even_y_bins), len(lines)-2]:
            pass
        else:
            lines[i] += mod_func("" + " "*len(y_tick_1) + "  ")

    # x ticks
    # print("DEBUG: x_bin_limits: ", x_bin_limits)
    # print("DEBUG: x_tick_indicies: ", x_tick_indicies)
    x_tick_labels = [ "{}".format(floatf.format(x_bin_limits[i])) for i in x_tick_indicies ]
    # print("DEBUG: x_tick_labels: ", x_tick_labels)
    x_ticks = ""
    for i in range(n_x_ticks):
        tick_label = x_tick_labels[i]
        x_ticks += tick_label
        if i == 0:
            x_ticks += " "    
        if i == (n_x_ticks-1):
            break
        bin_diff = x_tick_indicies[i+1] - x_tick_indicies[i]
        x_ticks += " " * ((bin_diff * 2) - len(tick_label))

    x_ticks = mod_func(x_ticks + "    ")
    lines.append(x_ticks)

    return lines


def get_filters_hdf5(data_file, filter_indices, read_slice=slice(0,-1,1)):

    dset_names = get_dataset_names(data_file)

    filter_names = []
    filter_datasets = []

    if filter_indices is not None:
        for filter_index in filter_indices:
            filter_name = dset_names[filter_index]
            filter_names.append(filter_name)
            filter_datasets.append(np.array(data_file[filter_name])[read_slice])

    return filter_names, filter_datasets


def apply_filters(datasets, filters):

    for filter_dset in filters:
        assert len(filters[0]) == len(filter_dset)

    joint_filter = np.array([np.all(l) for l in zip(*filters)], dtype=np.bool)

    filtered_datasets = []
    for dset in datasets:
        assert len(dset) == len(joint_filter)
        filtered_datasets.append(dset[joint_filter])

    return filtered_datasets


