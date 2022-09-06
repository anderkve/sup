# -*- coding: utf-8 -*-
import os
import numpy as np
from collections import OrderedDict
from scipy.stats import chi2
from io import StringIO 
import sup.defaults as defaults

class SupRuntimeError(Exception):
    """Exceptions class for sup runtime errors"""
    pass


def prettify(input_string, fg_ccode, bg_ccode, bold=True, reset=True):
    # example: "\u001b[48;5;" + str(bg_ccode) + ";38;5;" + str(fg_ccode) + 
    #          "m" + input_string + "\u001b[0m"
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


def insert_line(new_line, new_line_width, old_lines_list, old_width, fg_ccode,
                bg_ccode, insert_pos=None):

    # If no insert position is given, append the line to the end of the list
    if insert_pos is None:
        insert_pos = len(old_lines_list)

    result_width = 0
    result_lines_list = old_lines_list

    if new_line_width <= old_width:
        new_line += prettify(" " * (old_width - new_line_width), fg_ccode,
                             bg_ccode)
        result_width = old_width
    else:
        for i in range(len(result_lines_list)):
            result_lines_list[i] += prettify(" " * (new_line_width - old_width),
                                             fg_ccode, bg_ccode)
        result_width = new_line_width

    result_lines_list.insert(insert_pos, new_line)

    return result_lines_list, result_width


def add_left_padding(plot_lines, fg_ccode, bg_ccode, left_padding=defaults.left_padding):

    for i,line in enumerate(plot_lines):
        plot_lines[i] = prettify(left_padding, fg_ccode, bg_ccode) + line

    return plot_lines


def fill_missing_bg(lines_1, width_1, lines_2, width_2, bg_ccode):
    width_diff = width_1 - width_2
    if width_diff > 0:
        for i,line in enumerate(lines_2):
            lines_2[i] += prettify(" " * width_diff, bg_ccode, bg_ccode)
    elif width_diff < 0:
        for i,line in enumerate(lines_1):
            lines_1[i] += prettify(" " * int(abs(width_diff)), bg_ccode,
                                   bg_ccode)
    return lines_1, lines_2


def generate_legend(legend_entries, mod_func, sep="  ", internal_sep=" ",
                    left_padding=" "):

    legend = mod_func(left_padding, 0)
    legend_width = len(left_padding)

    for entry_tuple in legend_entries:
        marker, marker_ccode, txt, txt_ccode = entry_tuple
        if marker != "":
            legend += mod_func(marker, marker_ccode)
            legend += mod_func(internal_sep + txt, txt_ccode)
            legend_width += len(marker) + len(internal_sep)
        else:
            legend += mod_func(txt, txt_ccode)
        legend += mod_func(sep, txt_ccode)
        legend_width += len(txt) + len(sep)

    return legend, legend_width


def generate_colorbar_2(plot_lines, fig_width, ff,
                        ccodes, color_z_lims,
                        fg_ccode, bg_ccode, empty_bin_ccode):

    legend_mod_func = lambda input_str, input_fg_ccode : prettify(
        input_str, input_fg_ccode, bg_ccode, bold=True)

    # - colorbar
    cb_entries = []
    cb_entries.append(("", fg_ccode, "", fg_ccode))
    n_color_lims = len(color_z_lims)
    for i in range(0, n_color_lims):
        bar_ccode = fg_ccode
        if i % 2 == 1:
            bar_ccode = empty_bin_ccode

        if i < (n_color_lims - 1):
            cb_entries.append(("|", bar_ccode, 6*"■", ccodes[i]))
        else:
            cb_entries.append(("|", bar_ccode, "", fg_ccode))

    cb_line, cb_width = generate_legend(cb_entries, legend_mod_func, sep=" ",
                                        internal_sep="")

    plot_lines, fig_width = insert_line("", 0, plot_lines, fig_width, fg_ccode,
                                        bg_ccode)
    plot_lines, fig_width = insert_line(cb_line, cb_width, plot_lines,
                                        fig_width, fg_ccode, bg_ccode)

    # - numbers below the colorbar
    cb_nums_entries = []
    for i in range(0, n_color_lims):
        txt = ff.format(color_z_lims[i])
        if i % 2 == 0:
            cb_nums_entries.append(("", fg_ccode, txt, fg_ccode))
        else:
            gap_length = 8
            if len(txt) > gap_length:
                gap_length = gap_length - (len(txt) - gap_length) 
            cb_nums_entries.append(("", fg_ccode, " " * gap_length, fg_ccode))

    cb_nums_line, cb_nums_width = generate_legend(cb_nums_entries,
                                                  legend_mod_func,
                                                  sep="", internal_sep="")

    plot_lines, fig_width = insert_line(cb_nums_line, cb_nums_width, plot_lines,
                                        fig_width, fg_ccode, bg_ccode)

    return plot_lines, fig_width


def generate_colorbar(plot_lines, fig_width, ff,
                      ccs, color_z_lims):

    return generate_colorbar_2(plot_lines, fig_width, ff, ccs.ccodes, 
                               color_z_lims, ccs.fg_ccode, ccs.bg_ccode, 
                               ccs.empty_bin_ccode)


def generate_info_text(ff2, x_label, x_range, x_bin_width=None,
                       y_label=None, y_range=None, y_bin_width=None,
                       z_label=None, z_range=None, 
                       x_transf_expr="", y_transf_expr="", z_transf_expr="", 
                       y_normalized_hist=False, z_normalized_hist=False,
                       s_label=None, s_type=None, s_transf_expr="", 
                       w_label=None, w_transf_expr="",
                       capped_z=False, capped_label="z-axis", cap_val=1e99,
                       filter_names=[],
                       mode_name=None,
                       left_padding=defaults.left_padding + " "):

    info_lines = []
    info_lines.append(left_padding)

    line = left_padding
    line += "x-axis: {}".format(x_label)
    info_lines.append(line)
    if x_transf_expr != "":
        line = left_padding
        line += "  - transf.: {}".format(x_transf_expr)
        info_lines.append(line)
    if x_bin_width is not None:
        line = left_padding
        line += "  - bin width: {}".format(ff2.format(x_bin_width))
        info_lines.append(line)
    line = left_padding 
    line += "  - range: [{}, {}]".format(ff2.format(x_range[0]),
                                         ff2.format(x_range[1])) 
    info_lines.append(line)
        

    if y_label is not None:
        line = left_padding
        line += "y-axis: {}".format(y_label)
        info_lines.append(line)
        if y_transf_expr != "":
            line = left_padding 
            line += "  - transf.: {}".format(y_transf_expr)
            info_lines.append(line)
        if y_normalized_hist:
            line = left_padding + "  - normalized"
            info_lines.append(line)
        if y_bin_width is not None:
            line = left_padding
            line += "  - bin width: {}".format(ff2.format(y_bin_width))
            info_lines.append(line)
        if y_range is not None:
            line = left_padding
            line += "  - range: [{}, {}]".format(ff2.format(y_range[0]),
                                                 ff2.format(y_range[1]))
            info_lines.append(line)

    if z_label is not None:
        line = left_padding
        line += "z-axis: {}".format(z_label)
        info_lines.append(line)
        if z_transf_expr != "":
            line = left_padding
            line += "  - transf.: {}".format(z_transf_expr)
            info_lines.append(line)
        if z_normalized_hist:
            line = left_padding + "  - normalized"
            info_lines.append(line)
        if z_range is not None:
            line = left_padding
            line += "  - range: [{}, {}]".format(ff2.format(z_range[0]),
                                                 ff2.format(z_range[1]))
            info_lines.append(line)

    if (s_label is not None) and (s_type is not None):
        line = left_padding
        line += "sort: {} [{}]".format(s_label, s_type)
        info_lines.append(line)
        if s_transf_expr != "":
            line = left_padding
            line += "  - transf.: {}".format(s_transf_expr)
            info_lines.append(line)

    if w_label is not None:
        line = left_padding
        line += "weights: {}".format(w_label)
        info_lines.append(line)
        if w_transf_expr != "":
            line = left_padding
            line += "  - transf.: {}".format(w_transf_expr)
            info_lines.append(line)

    if capped_z:
        line = left_padding
        line += "capped: {} dataset capped at {}".format(capped_label,
                                                         ff2.format(cap_val))
        info_lines.append(line)

    for f_name in filter_names:
        line = left_padding + "filter: {}".format(f_name)
        info_lines.append(line)

    if mode_name is not None:
        info_lines.append(left_padding)
        line = left_padding + "plot type: {}".format(mode_name)
        info_lines.append(line)

    info_lines.append(left_padding)

    return info_lines



def add_info_text(plot_lines, fig_width, fg_ccode, bg_ccode,
                  ff2, x_label, x_range, x_bin_width=None,
                  y_label=None, y_range=None, y_bin_width=None,
                  z_label=None, z_range=None, 
                  x_transf_expr="", y_transf_expr="", z_transf_expr="", 
                  y_normalized_hist=False, z_normalized_hist=False,
                  s_label=None, s_type=None, s_transf_expr="", 
                  w_label=None, w_transf_expr="",
                  capped_z=False, capped_label="z-axis", cap_val=1e99,
                  filter_names=[],
                  mode_name=None,
                  left_padding=defaults.left_padding + " "):

    info_lines = generate_info_text(ff2, 
                                    x_label,
                                    x_range, 
                                    x_bin_width=x_bin_width,
                                    y_label=y_label, 
                                    y_range=y_range, 
                                    y_bin_width=y_bin_width,
                                    z_label=z_label,
                                    z_range=z_range, 
                                    x_transf_expr=x_transf_expr, 
                                    y_transf_expr=y_transf_expr,
                                    z_transf_expr=z_transf_expr,
                                    y_normalized_hist=y_normalized_hist,
                                    z_normalized_hist=z_normalized_hist,
                                    s_label=s_label,
                                    s_type=s_type, 
                                    s_transf_expr=s_transf_expr,
                                    w_label=w_label,
                                    w_transf_expr=w_transf_expr,
                                    capped_z=capped_z,
                                    capped_label=capped_label,
                                    cap_val=cap_val,
                                    filter_names=filter_names,
                                    mode_name=mode_name,
                                    left_padding=left_padding)

    for i,line in enumerate(info_lines):
        pretty_line = prettify(line + "  ", fg_ccode, bg_ccode, bold=False)
        plot_lines, fig_width = insert_line(pretty_line, len(line),
                                            plot_lines, fig_width, 
                                            fg_ccode, bg_ccode)

    return plot_lines, fig_width


def get_dataset_names_hdf5(hdf5_file_object):
    import h5py
    result = []
    def get_datasets(name, obj):
        if type(obj) is h5py._hl.dataset.Dataset:
            result.append(name)

    hdf5_file_object.visititems(get_datasets)
    return result


def get_dataset_names_txt(txt_file_name):
    result = []

    # To avoid reading the entire file just to list the dataset names
    # we'll use a StringIO file-like object constructed from the first
    # interesting line in the file.

    comments = '#'

    # Let's find the first non-empty comment line, which we require 
    # should contain the column names.
    firstline = ''
    with open(txt_file_name) as f:
        templine = ''
        for line in f:
            templine = line.lstrip().rstrip()
            if not ((templine == '') or (templine == comments)):
                break
        firstline = templine

    use_names = True
    # If firstline is not a header with column names, we have to create
    # a list of names based on the number of columns we detect from firstline.
    if not firstline.startswith(comments):
        n_cols = len(firstline.replace(',', ' ').split())
        use_names = ['dataset' + str(i) for i in range(n_cols)]

    stringIO_file = StringIO(firstline)
    dsets = np.genfromtxt(stringIO_file, names=use_names, comments=comments)
    result = dsets.dtype.names

    return result


def check_file_type(input_file):
    """Determine file type based on file extension

    Args:
        input_file (string): The input file path.

    Returns:
        file_type (string): The identified file type. Can be "text" or "hdf5".

    """

    # Default assumption is that the input file is a text file.
    file_type = "text"

    filename_without_extension, file_extension = os.path.splitext(input_file)    

    if file_extension in ['.hdf5', '.h5', '.he5']:
        file_type = "hdf5"

    return file_type


def read_input_file(input_file, dset_indices, read_slice, delimiter=' '):
    dsets = []
    dset_names = []

    file_type = check_file_type(input_file)

    if file_type == "text":
        print("Reading " + input_file + " as a text file with delimiter '" +
              delimiter + "'")
        print()
        dsets, dset_names = read_input_file_txt(input_file, dset_indices,
                                                read_slice, delimiter)

    elif file_type == "hdf5":
        print("Reading " + input_file + " as an HDF5 file")
        print()
        dsets, dset_names = read_input_file_hdf5(input_file, dset_indices,
                                                 read_slice)

    return dsets, dset_names    



def read_input_file_hdf5(input_file, dset_indices, read_slice):
    import h5py
    dsets = []
    dset_names = []

    f = h5py.File(input_file, "r")

    all_dset_names = get_dataset_names_hdf5(f)

    dset_names = [all_dset_names[dset_index] for dset_index in dset_indices]

    dsets = [np.array(f[dset_name])[read_slice] for dset_name in dset_names]

    f.close()

    return dsets, dset_names    



def read_input_file_txt(input_file, dset_indices, read_slice, delimiter):
    dsets = []
    dset_names = []

    all_dset_names = get_dataset_names_txt(input_file)

    dset_names = [all_dset_names[dset_index] for dset_index in dset_indices]
    
    if delimiter.strip() == "":
        delimiter = None

    dsets = list(np.genfromtxt(input_file, usecols=dset_indices,
                                names=dset_names, unpack=True, comments="#", 
                                delimiter=delimiter))
    if len(dset_indices) == 1:
        dsets = [dsets]

    return dsets, dset_names    



def get_filters(input_file, filter_indices, read_slice, delimiter=' '):
    filter_dsets = []
    filter_names = []

    # @todo: Check this before function is called?
    if filter_indices is None:
        return filter_dsets, filter_names

    file_type = check_file_type(input_file)

    if file_type == "text":
        filter_dsets, filter_names = get_filters_txt(input_file,
                                                     filter_indices,
                                                     read_slice,
                                                     delimiter)
    elif file_type == "hdf5":
        filter_dsets, filter_names = get_filters_hdf5(input_file, 
                                                      filter_indices, 
                                                      read_slice)        

    return filter_dsets, filter_names


def get_filters_hdf5(input_file, filter_indices, read_slice=slice(0,-1,1)):
    import h5py
    filter_dsets = []
    filter_names = []

    f = h5py.File(input_file, "r")

    dset_names = get_dataset_names_hdf5(f)

    if filter_indices is not None:
        for filter_index in filter_indices:
            filter_name = dset_names[filter_index]
            filter_names.append(filter_name)
            filter_dsets.append(np.array(f[filter_name])[read_slice])

    f.close()

    return filter_dsets, filter_names


def get_filters_txt(input_file, filter_indices, read_slice, delimiter=' '):
    filter_dsets = []
    filter_names = []

    all_dset_names = get_dataset_names_txt(input_file)

    filter_names = [
        all_dset_names[filter_index] for filter_index in filter_indices
    ]
    
    if delimiter.strip() == "":
        delimiter = None

    filter_dsets = list(np.genfromtxt(input_file, usecols=filter_indices,
                                       names=filter_names, unpack=True, 
                                       comments="#", delimiter=delimiter))
    if len(filter_indices) == 1:
        filter_dsets = [filter_dsets]

    return filter_dsets, filter_names


def apply_filters(datasets, filters):

    for filter_dset in filters:
        assert len(filters[0]) == len(filter_dset)

    joint_filter = np.array([np.all(l) for l in zip(*filters)], dtype=np.bool)

    filtered_datasets = []
    for dset in datasets:
        assert len(dset) == len(joint_filter)
        filtered_datasets.append(dset[joint_filter])

    if len(filtered_datasets[0]) == 0:
        raise SupRuntimeError("No data points left after applying filters.")

    return filtered_datasets



def get_bin_tuples_maxmin_1d(x_data, y_data, xy_bins, x_range, y_range, s_data,
                             s_type, fill_below=False, fill_z_val=-1, 
                             split_marker=False, return_function_data=False,
                             fill_y_val=np.nan):

    assert s_type in ["min", "max"]
    assert len(x_data) == len(y_data)
    data_length = len(x_data)

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range
    y_min, y_max = y_range

    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)
    y_bin_limits = np.linspace(y_min, y_max, y_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    # Digitize x data
    xdata_xbin_numbers = np.digitize(x_data, x_bin_limits)
    xdata_xbin_numbers -= 1

    # Prepare dictionary: x_bin_index --> {"x_centre": ..., 
    #                                      "y_vals": [...], 
    #                                      "s_vals": [...]}
    x_bins_dict = OrderedDict()
    for x_bin_number in range(x_bins):
        bin_key = x_bin_number
        x_bins_dict[bin_key] = {}
        x_bins_dict[bin_key]["x_centre"] = x_bin_centres[x_bin_number]
        x_bins_dict[bin_key]["y_vals"] = []
        x_bins_dict[bin_key]["s_vals"] = []

    # Fill the arrays "y_vals" and "s_vals" for each bin
    for di in range(data_length):

        y_val = y_data[di]
        s_val = s_data[di]

        x_bin_number = xdata_xbin_numbers[di]

        bin_key = x_bin_number

        if bin_key in x_bins_dict.keys():

            x_bins_dict[bin_key]["y_vals"].append(y_val)
            x_bins_dict[bin_key]["s_vals"].append(s_val)

    # Convert to numpy arrays
    for bin_key in x_bins_dict.keys():
        x_bins_dict[bin_key]["y_vals"] = \
            np.array(x_bins_dict[bin_key]["y_vals"])
        x_bins_dict[bin_key]["s_vals"] = \
            np.array(x_bins_dict[bin_key]["s_vals"])


    # For each bin, sort the arrays according to s_data dataset
    new_xdata = []
    new_ydata = []
    for bin_key in x_bins_dict.keys():

        # Get data index of the z-value for this bin, based on s_data sorting
        ordering = None
        ordering_low_to_high = np.argsort(x_bins_dict[bin_key]["s_vals"])
        if s_type == "max":
            ordering = ordering_low_to_high[::-1]
        elif s_type == "min":
            ordering = ordering_low_to_high

        x_bins_dict[bin_key]["y_vals"] = \
            x_bins_dict[bin_key]["y_vals"][ordering]

        new_xdata.append(x_bin_centres[bin_key])
        if len(x_bins_dict[bin_key]["y_vals"]) > 0:
            new_ydata.append(x_bins_dict[bin_key]["y_vals"][0])
        else:
            new_ydata.append(fill_y_val)

    new_xdata = np.array(new_xdata)
    new_ydata = np.array(new_ydata)

    # Digitize new x and y data
    new_xdata_xbin_numbers = np.digitize(new_xdata, x_bin_limits)
    new_xdata_xbin_numbers -= 1
    new_ydata_ybin_numbers = np.digitize(new_ydata, y_bin_limits, right=True)
    new_ydata_ybin_numbers -= 1

    # Create result dict
    result_dict = OrderedDict()
    assert len(new_xdata_xbin_numbers) == len(new_ydata_ybin_numbers)
    for i in range(len(new_xdata_xbin_numbers)):

        x_bin_number = new_xdata_xbin_numbers[i]
        y_bin_number = new_ydata_ybin_numbers[i]

        if y_bin_number >= y_bins:
            continue

        bin_key = (x_bin_number, y_bin_number)
        if split_marker:
            use_z_val = 1
            if new_ydata[i] > y_bin_centres[y_bin_number]:
                use_z_val = 2
            result_dict[bin_key] = (x_bin_centres[x_bin_number],
                                    y_bin_centres[y_bin_number], use_z_val)
        else:
            result_dict[bin_key] = (x_bin_centres[x_bin_number], 
                                    y_bin_centres[y_bin_number], 1)

        # Fill bins below the (x,y) bin of the actual function value
        if fill_below:
            for ybn in range(y_bin_number-1, -1, fill_z_val):
                bin_key = (x_bin_number, ybn)
                result_dict[bin_key] = (x_bin_centres[x_bin_number],
                                        y_bin_centres[ybn], -1)

    if return_function_data:
        return result_dict, x_bin_limits, y_bin_limits, new_xdata, new_ydata
    else:
        return result_dict, x_bin_limits, y_bin_limits


def get_bin_tuples_maxmin(x_data, y_data, z_data, xy_bins, x_range, y_range,
                          s_data, s_type):

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

    # Prepare dictionary: (x_bin_index, y_bin_index) --> [(z_val, data_index), 
    #                                                     (z_val, data_index), 
    #                                                     ...]
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
        bins_dict[bin_key]["data_indices"] = \
            np.array(bins_dict[bin_key]["data_indices"])

    # For each bin, sort the arrays according to s_data dataset
    result_dict = OrderedDict()
    for bin_key in bins_dict.keys():

        # Get data index of the z-value for this bin, based on s_data sorting
        ordering = None
        ordering_low_to_high = np.argsort(bins_dict[bin_key]["s_vals"])
        if s_type == "max":
            ordering = ordering_low_to_high[::-1]
        elif s_type == "min":
            ordering = ordering_low_to_high

        bins_dict[bin_key]["z_vals"] = bins_dict[bin_key]["z_vals"][ordering]
        bins_dict[bin_key]["data_indices"] = \
            bins_dict[bin_key]["data_indices"][ordering]

        if len(bins_dict[bin_key]["z_vals"]) > 0:

            result_dict[bin_key] = (x_bin_centres[bin_key[0]], 
                                    y_bin_centres[bin_key[1]], 
                                    bins_dict[bin_key]["z_vals"][0], 
                                    bins_dict[bin_key]["data_indices"][0])

    return result_dict, x_bin_limits, y_bin_limits


def get_bin_tuples_avg_1d(x_data, y_data, xy_bins, x_range, y_range,
                          fill_below=False, fill_z_val=-1, split_marker=False):

    assert len(x_data) == len(y_data)
    data_length = len(x_data)

    x_bins, y_bins = xy_bins
    x_min, x_max = x_range
    y_min, y_max = y_range

    x_bin_limits = np.linspace(x_min, x_max, x_bins + 1)
    y_bin_limits = np.linspace(y_min, y_max, y_bins + 1)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    # Digitize x data
    xdata_xbin_numbers = np.digitize(x_data, x_bin_limits) - 1

    # Prepare dictionary: x_bin_index --> {"x_centre": ...,
    #                                      "y_vals": [...],
    #                                      "s_vals": [...]}
    x_bins_dict = OrderedDict()
    for x_bin_number in range(x_bins):
        bin_key = x_bin_number
        x_bins_dict[bin_key] = {}
        x_bins_dict[bin_key]["x_centre"] = x_bin_centres[x_bin_number]
        x_bins_dict[bin_key]["y_vals"] = []

    # Fill the array "y_vals"
    for di in range(data_length):

        y_val = y_data[di]

        x_bin_number = xdata_xbin_numbers[di]

        bin_key = x_bin_number

        if bin_key in x_bins_dict.keys():

            x_bins_dict[bin_key]["y_vals"].append(y_val)

    # Convert to numpy arrays
    for bin_key in x_bins_dict.keys():
        x_bins_dict[bin_key]["y_vals"] = \
            np.array(x_bins_dict[bin_key]["y_vals"])


    # For each bin, calculate the average y value. Fill new datasets:
    # - new_xdata: dataset with the x bin centers of non-empty bins
    # - new_ydata: the corrsponding average y values for each x bin
    new_xdata = []
    new_ydata = []
    for bin_key in x_bins_dict.keys():

        if len(x_bins_dict[bin_key]["y_vals"]) > 0:

            new_xdata.append(x_bin_centres[bin_key])
            new_ydata.append(np.average(x_bins_dict[bin_key]["y_vals"]))

    new_xdata = np.array(new_xdata)
    new_ydata = np.array(new_ydata)

    # Digitize new x and y data
    new_xdata_xbin_numbers = np.digitize(new_xdata, x_bin_limits)
    new_xdata_xbin_numbers -= 1
    new_ydata_ybin_numbers = np.digitize(new_ydata, y_bin_limits, right=True)
    new_ydata_ybin_numbers -= 1

    # Create result dict
    result_dict = OrderedDict()
    assert len(new_xdata_xbin_numbers) == len(new_ydata_ybin_numbers)
    for i in range(len(new_xdata_xbin_numbers)):

        x_bin_number = new_xdata_xbin_numbers[i]
        y_bin_number = new_ydata_ybin_numbers[i]

        if y_bin_number >= y_bins:
            continue

        bin_key = (x_bin_number, y_bin_number)
        if split_marker:
            use_z_val = 1
            if new_ydata[i] > y_bin_centres[y_bin_number]:
                use_z_val = 2
            result_dict[bin_key] = (x_bin_centres[x_bin_number],
                                    y_bin_centres[y_bin_number], use_z_val)
        else:
            result_dict[bin_key] = (x_bin_centres[x_bin_number],
                                    y_bin_centres[y_bin_number], 1)

        # Fill bins below the (x,y) bin of the actual function value
        if fill_below:
            for ybn in range(y_bin_number-1, -1, fill_z_val):
                bin_key = (x_bin_number, ybn)
                result_dict[bin_key] = (
                    x_bin_centres[x_bin_number],
                    y_bin_centres[ybn], 
                    -1
                )

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

    # Prepare dictionary: (x_bin_index, y_bin_index) --> [(z_val, data_index),
    #                                                     (z_val, data_index),
    #                                                     ...]
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


def add_axes(lines, xy_bins, x_bin_limits, y_bin_limits, mod_func=None,
             mod_func_2=None, floatf="{: .1e}", add_y_grid_lines=False):

    if mod_func is None:
        mod_func = lambda x : x

    x_tick_indicies = []
    tick_spacing = 0
    tick_width = len("{}".format(floatf.format(0.0)))
    for n_ticks in range(2,100):
        new_indicies = [
            int(i) for i in np.floor(np.linspace(0, xy_bins[0], n_ticks))
        ]
        tick_spacing = (new_indicies[1] - new_indicies[0]) * 2
        if tick_spacing < tick_width + 1:
            break
        x_tick_indicies = new_indicies
    n_x_ticks = len(x_tick_indicies)


    max_y_ticks = int(np.ceil(xy_bins[1] / 2.))
    min_y_ticks = int(np.floor(xy_bins[1] / 10.) + 3)
    yx_bins_ratio = float(xy_bins[1]) / xy_bins[0]
    n_y_ticks = min(max_y_ticks, int(np.ceil(n_x_ticks * yx_bins_ratio))) 
    n_y_ticks = max(n_y_ticks, min_y_ticks) 
    y_tick_indicies = [
        int(i) for i in np.floor(np.linspace(0, xy_bins[1], n_y_ticks))
    ]

    # Reverse the list of indices, since we're printing the plot from top down
    y_tick_indicies = y_tick_indicies[::-1]


    #
    # Add axis lines
    #

    top_line = mod_func(" " + "  " * xy_bins[0] + "_")
    lines = [top_line] + lines
    for i in range(len(lines)):
        if i == 0:
            continue
        if i in y_tick_indicies:
            lines[i] = lines[i] + mod_func("│\u0332")
        else:
            lines[i] += mod_func("│")

    # x axis:
    x_axis = " "
    for i in range(n_x_ticks):
        if i == 0:
            x_axis += "┼─"
        elif i == (n_x_ticks-1):
            x_axis += "┼"
            break
        else:
            x_axis += "┼─"
        bin_diff = x_tick_indicies[i+1] - x_tick_indicies[i]
        x_axis += "─" * (bin_diff * 2 - 2)
    x_axis = mod_func(x_axis)
    lines.append(x_axis)

    #
    # Add x and y ticks
    #

    # y ticks
    y_tick_labels = []
    for i in y_tick_indicies:
        label = "{}".format(floatf.format(y_bin_limits[::-1][i]))
        y_tick_labels.append(label)


    if add_y_grid_lines:
        for i, tick_index in enumerate(y_tick_indicies):
            # top line
            if tick_index == y_tick_indicies[-1]:
                new_line = mod_func_2(" " + " _" * xy_bins[0]) + mod_func("_")
                lines[tick_index] = new_line
            # other lines
            else:
                new_line = lines[tick_index].replace("  ", mod_func_2(" _"))
                lines[tick_index] = new_line

            # Add y tick
            lines[tick_index] += mod_func("" + y_tick_labels[i] + "   ")
    else:
        for i, tick_index in enumerate(y_tick_indicies):
            lines[tick_index] += mod_func("" + y_tick_labels[i] + "   ")


    for i,line in enumerate(lines):
        if i in y_tick_indicies:
            pass
        else:
            lines[i] += mod_func("" + " "*tick_width + "   ")

    # x ticks
    x_tick_labels = []
    for i in x_tick_indicies:
        label = "{}".format(floatf.format(x_bin_limits[i]))
        x_tick_labels.append(label)
    x_ticks = ""
    for i in range(n_x_ticks):
        tick_label = x_tick_labels[i]
        x_ticks += tick_label
        if i == (n_x_ticks-1):
            break
        bin_diff = x_tick_indicies[i+1] - x_tick_indicies[i]
        x_ticks += " " * ((bin_diff * 2) - len(tick_label))

    x_ticks = mod_func(x_ticks + "     ")
    lines.append(x_ticks)

    return lines


def get_cl_included_bins_1d(confidence_levels, y_func_data, dx):

    included_bins = []

    # Check assumption that the max (non-NaN) element is 1.0
    assert np.max(y_func_data[np.invert(np.isnan(y_func_data))]) == 1.0

    indices = list(range(len(y_func_data)))

    for cl in confidence_levels:

        # Shortcut for 100% region
        if cl >= 100.0:
            included_bins.append(indices)
            continue

        # Calculate the correct L/L_max threshold for the given CL
        pp = cl * 0.01
        chi2_val = chi2.ppf(pp, df=1)
        llhratio_thres = np.exp(-0.5 * chi2_val)

        inc_bins = []

        for index in indices:

            y_val = y_func_data[index]

            if np.isnan(y_val):
                continue

            if y_val >= llhratio_thres:
                inc_bins.append(index)
            
        included_bins.append(inc_bins)

    return included_bins


def get_cr_included_bins_1d(credible_regions, bins_content, dx):

    included_bins = []

    # ordering for sorting from high to low bin content
    ordering = np.argsort(bins_content)[::-1]

    for cr in credible_regions:

        # Shortcut for 100% region
        if cr >= 100.0:
            included_bins.append(ordering)
            continue

        cr_sum = 0.0
        inc_bins = []

        n_indicies = len(ordering)
        for i,index in enumerate(ordering):
            bc = bins_content[index]
            cr_sum += bc * dx * 100

            inc_bins.append(index)

            if (cr_sum > cr):
                break

            if i < n_indicies - 1:
                next_index = ordering[i+1]
                next_bc = bins_content[next_index]
                next_cr_sum = cr_sum + (next_bc * dx * 100)
                if np.abs(cr_sum - cr) < np.abs(next_cr_sum -cr):
                    break
            
        included_bins.append(inc_bins)

    return included_bins


def get_ranges_from_included_bins(included_bins, bin_limits):

    result_bin_indices = []
    result_positions = []
    for inc_bins_list in included_bins:

        # print("START new CR: inc_bins_list: ", inc_bins_list)
        ranges_bin_indices = []
        ranges_positions = []

        inc_bins_list.sort()

        inside = False
        begin_bi = 0
        end_bi = 0
        n_bins = len(inc_bins_list)

        for i,bi in enumerate(inc_bins_list):
            # print("i: ", i, "   bi: ", bi, "  inside: ", inside)
            if inside:
                # print(" - inc_bins_list[i+1] = ", inc_bins_list[i+1])
                if i == n_bins-1:
                    end_bi = bi+1
                    ranges_bin_indices.append((begin_bi, end_bi))
                    ranges_positions.append((bin_limits[begin_bi],
                                             bin_limits[end_bi]))
                    inside = False
                    continue

                else:
                    if inc_bins_list[i+1] == bi+1:
                        # print(" - found next!")
                        continue
                    else:
                        # print(" - did not find next -- closing range")
                        end_bi = bi + 1
                        ranges_bin_indices.append((begin_bi, end_bi))
                        ranges_positions.append((bin_limits[begin_bi],
                                                 bin_limits[end_bi]))
                        inside = False
                        # continue
            # not inside
            else:
                begin_bi = bi
                inside = True
                if ((i < n_bins-1 and inc_bins_list[i+1] != bi+1) or 
                    i == n_bins-1):
                    end_bi = bi+1
                    ranges_bin_indices.append((begin_bi, end_bi))
                    ranges_positions.append((bin_limits[begin_bi],
                                             bin_limits[end_bi]))
                    inside = False

        result_bin_indices.append(ranges_bin_indices)
        result_positions.append(ranges_positions)

    return result_bin_indices, result_positions


def get_bar_str(ranges_pos, bin_limits):

    n_bins = len(bin_limits) - 1 
    bar_str = "   "
    prev_end_index = 0
    
    for bar_range in ranges_pos:

        indices = [0,0]
        indices[0] = np.where(bin_limits==bar_range[0])[0][0]
        indices[1] = np.where(bin_limits==bar_range[1])[0][0]

        x_tick_indicies = []
        n_ticks = 2
        new_indicies = []
        for i in np.floor(np.linspace(indices[0], indices[1], n_ticks)):
            new_indicies.append(int(i))
        x_tick_indicies = new_indicies
        n_x_ticks = len(x_tick_indicies)

        open_start = False
        if new_indicies[0] == 0:
            bar_str = " "
            open_start = True

        open_end = False
        if new_indicies[-1] == n_bins:
            open_end = True

        bar_str += "" + "  " * (new_indicies[0] - prev_end_index - 1)

        for ti in range(n_x_ticks):
            if ti == 0:
                if open_start:
                    bar_str += "╶─"
                else:
                    bar_str += "├─"
            elif ti == (n_x_ticks-1):
                if open_end:
                    bar_str += "╴ "
                else:
                    bar_str += "┤ "
                break
            bin_diff = x_tick_indicies[ti+1] - x_tick_indicies[ti]
            bar_str += "─" * (bin_diff * 2 - 2)

        prev_end_index = indices[1]

    return bar_str


def generate_credible_region_bars(credible_regions, bins_content, 
                                  bin_limits, ff2):

    cr_bar_lines = []

    dx = bin_limits[1] - bin_limits[0]

    included_bins = get_cr_included_bins_1d(credible_regions, bins_content, dx)

    cr_ranges_indices, cr_ranges_pos = \
        get_ranges_from_included_bins(included_bins, bin_limits)

    for cr_index,cr_val in enumerate(credible_regions):
        
        bar_str = get_bar_str(cr_ranges_pos[cr_index], bin_limits)

        bar_str += "{:.12g}% CR".format(cr_val)

        cr_bar_lines.append(bar_str)

    return cr_bar_lines


def generate_confidence_level_bars(confidence_levels, y_func_data,
                                   bin_limits, ff2):

    cl_bar_lines = []

    dx = bin_limits[1] - bin_limits[0]

    included_bins = get_cl_included_bins_1d(confidence_levels, y_func_data, dx)

    cl_ranges_indices, cl_ranges_pos = \
        get_ranges_from_included_bins(included_bins, bin_limits)

    for cl_index,cl_val in enumerate(confidence_levels):
        
        bar_str = get_bar_str(cl_ranges_pos[cl_index], bin_limits)

        bar_str += "{:.12g}% CI".format(cl_val)

        cl_bar_lines.append(bar_str)

    return cl_bar_lines


def check_weights(w_data, w_name=""):
    
    extra_info = ""
    if w_name != "":
        extra_info = "The current dataset for weights is {}.".format(w_name) 

    if np.any(w_data < 0.0):
        raise SupRuntimeError("Negative weights are not allowed. "
                              "Check the weights data set. " + extra_info)

    elif np.all(w_data <= 0.0):
        raise SupRuntimeError("Found no weights greater than zero. "
                              "Check the weights data set. " + extra_info)

    return 


def fill_plot(xy_bins, bins_info, ccs, ms, get_ccode_and_marker):

    plot_lines = []
    for yi in range(xy_bins[1]):

        yi_line = prettify(" ", ccs.fg_ccode, ccs.bg_ccode)

        for xi in range(xy_bins[0]):

            xiyi = (xi,yi)

            ccode = ccs.empty_bin_ccode
            marker = ms.empty_bin_marker

            if xiyi in bins_info.keys():

                ccode, marker = get_ccode_and_marker(xiyi)

            # Add point to line
            yi_line += prettify(marker, ccode, ccs.bg_ccode)

        plot_lines.append(yi_line)

    plot_lines.reverse()

    return plot_lines
