# -*- coding: utf-8 -*-
import os
import numpy as np
from collections import OrderedDict
from scipy.stats import chi2
from io import StringIO 
import sup.defaults as defaults


error_prefix = "sup error:"

class SupRuntimeError(Exception):
    """Exceptions class for sup runtime errors"""
    pass



def prettify(input_string, fg_ccode, bg_ccode, bold=True, reset=True):
    """Add pretty formatting for the input string.

    Args:
        input_string (string): The input string.

        fg_ccode (int): Foreground color code.

        bg_ccode (int): Background color code.
        
        bold (bool): Use bold text?

        reset (bool): Reset format at the end of the string?

    Returns:
        result (string): The formatted string

    """

    # Example: "\u001b[48;5;" + str(bg_ccode) + ";38;5;" + str(fg_ccode) + 
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
    """Insert a new formatted line (string) in an existing list of lines.

    Args:
        new_line (string): The new line

        new_line_width (int): The length of the new line without any formatting.

        old_lines_list (list of strings): The collection of existing lines.

        old_width (int): Length of the longest (unformatted) existing line.

        fg_ccode (int): Foreground color code.

        bg_ccode (int): Background color code.
        
        insert_pos (int): List index where new_line should be inserted.

    Returns:
        result_lines_list (list of strings): The new collection of lines.

    """

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



def add_left_padding(plot_lines, fg_ccode, bg_ccode, 
                     left_padding=defaults.left_padding):
    """Add blank spaces on the left-hand side of the given lines.

    Args:
        plot_lines (list of strings): The collection of lines.

        fg_ccode (int): Foreground color code.

        bg_ccode (int): Background color code.
        
        left_padding (int): The number of spaces to add.

    Returns:
        plot_lines (list of strings): The new collection of lines.

    """

    for i,line in enumerate(plot_lines):
        plot_lines[i] = prettify(left_padding, fg_ccode, bg_ccode) + line

    return plot_lines



def generate_legend(legend_entries, bg_ccode, sep="  ", internal_sep=" ",
                    left_padding=" "):
    """Generate a plot legend line.

    Args:
        legend_entries (list of tuples): A list with one tuple for each
        entry in the legend. Each tuple is of the form (marker, marker_ccode, 
        txt, txt_ccode)

        bg_ccode (int): Background color code.

        sep (string): String used to separate legend entries.

        internal_sep (string): String used to separate the marker and the text
            in a legend entry.

        left_padding (string): Whitespace string used for left padding.

    Returns:
        legend (string): The constructed legend line.

        legend_width (int): The width of the legend line

    """

    mod_func = lambda input_str, input_fg_ccode : prettify(
        input_str, input_fg_ccode, bg_ccode, bold=True)

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



def generate_colorbar(plot_lines, fig_width, ff, ccs, color_z_lims):
    """Generate a color bar and add it to the plot_lines.

    This function constructs a color bar legend, including the color
    swatches and corresponding numerical labels, and appends it to the
    existing plot lines. It also adjusts the figure width if the
    colorbar is wider than the current figure.

    Args:
        plot_lines (list of strings): The collection of lines representing the plot
            onto which the colorbar will be added. Each string is a line of the plot.
        fig_width (int): The current width of the figure (in characters). This
            may be updated if the colorbar is wider.
        ff (string): Format string for floats used to format the numerical labels
            on the colorbar (e.g., "{:.2f}").
        ccs (CCodeSettings): An object or dictionary containing color code settings,
            specifically:
            - ccs.ccodes: A list of color codes for the color swatches.
            - ccs.fg_ccode: The foreground color code for text and non-swatch elements.
            - ccs.bg_ccode: The background color code for the plot area.
            - ccs.empty_bin_ccode: Color code for elements like separators if needed.
        color_z_lims (list of floats): A list of float values representing the
            boundaries for each color in the color bar. These are the numerical
            values that will be labeled on the colorbar.

    Returns:
        tuple:
            - plot_lines (list of strings): The updated collection of lines with the
              colorbar added.
            - fig_width (int): The potentially updated width of the figure after
              adding the colorbar.
    """

    ccodes = ccs.ccodes
    fg_ccode = ccs.fg_ccode
    bg_ccode = ccs.bg_ccode
    empty_bin_ccode = ccs.empty_bin_ccode

    # Construct entries for the colorbar display.
    # Each entry is a tuple: (marker, marker_ccode, text, text_ccode)
    # The first entry is empty, acting as a spacer or start point.
    cb_entries = []
    cb_entries.append(("", fg_ccode, "", fg_ccode)) # Initial empty entry for alignment/padding.
    n_color_lims = len(color_z_lims)

    # Loop through color limits to create color swatches and separators.
    for i in range(0, n_color_lims):
        bar_ccode = fg_ccode # Default color for separator.
        if i % 2 == 1:
            bar_ccode = empty_bin_ccode

        # Add a color swatch (■■■■■■) and its preceding separator (|).
        # The last limit doesn't get a swatch after it, just a final separator.
        if i < (n_color_lims - 1):
            cb_entries.append(("|", bar_ccode, 6*"■", ccodes[i])) # Separator, then color swatch.
        else:
            cb_entries.append(("|", bar_ccode, "", fg_ccode)) # Final separator.

    # Generate the colorbar line string using the helper function generate_legend.
    cb_line, cb_width = generate_legend(cb_entries, bg_ccode, sep=" ",
                                        internal_sep="")

    # Insert a blank line before the colorbar for spacing.
    plot_lines, fig_width = insert_line("", 0, plot_lines, fig_width, fg_ccode,
                                        bg_ccode)
    # Insert the generated colorbar line into the plot_lines.
    plot_lines, fig_width = insert_line(cb_line, cb_width, plot_lines,
                                        fig_width, fg_ccode, bg_ccode)

    # Construct entries for the numerical labels below the colorbar.
    cb_nums_entries = []
    for i in range(0, n_color_lims):
        txt = ff.format(color_z_lims[i]) # Format the numerical limit.
        # Add the formatted number for even indices.
        if i % 2 == 0:
            cb_nums_entries.append(("", fg_ccode, txt, fg_ccode))
        # For odd indices, add spacing to align numbers under swatch boundaries.
        # This creates gaps between numbers if they are too close.
        else:
            gap_length = 8
            if len(txt) > gap_length: # Adjust gap if text is too long.
                gap_length = gap_length - (len(txt) - gap_length)
            cb_nums_entries.append(("", fg_ccode, " " * gap_length, fg_ccode))

    # Generate the line string for colorbar numbers.
    cb_nums_line, cb_nums_width = generate_legend(cb_nums_entries,
                                                  bg_ccode,
                                                  sep="", internal_sep="")

    # Insert the colorbar numbers line into plot_lines.
    plot_lines, fig_width = insert_line(cb_nums_line, cb_nums_width, plot_lines,
                                        fig_width, fg_ccode, bg_ccode)

    return plot_lines, fig_width




def generate_info_text(ff=defaults.ff2, 
                       x_label=None, x_range=None, x_bin_width=None,
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
    """Generate the info text printed below the plot.

    This function compiles various pieces of information about the plot
    (axes, transformations, filters, etc.) into a list of formatted strings.
    These strings are intended to be displayed below the main plot area, providing
    context and details about the data shown.

    Args:
        ff (string, optional): Format string for floating-point numbers.
            Defaults to `defaults.ff2`.
        x_label (string, optional): Label for the X-axis.
        x_range (tuple of floats, optional): Min and max values for the X-axis range.
        x_bin_width (float, optional): Width of bins along the X-axis (for histograms).
        y_label (string, optional): Label for the Y-axis.
        y_range (tuple of floats, optional): Min and max values for the Y-axis range.
        y_bin_width (float, optional): Width of bins along the Y-axis (for histograms).
        z_label (string, optional): Label for the Z-axis (e.g., for 2D histograms or color values).
        z_range (tuple of floats, optional): Min and max values for the Z-axis range.
        x_transf_expr (string, optional): Python expression string used to transform X-axis data.
        y_transf_expr (string, optional): Python expression string used to transform Y-axis data.
        z_transf_expr (string, optional): Python expression string used to transform Z-axis data.
        y_normalized_hist (bool, optional): True if the 1D histogram on Y-axis is normalized.
        z_normalized_hist (bool, optional): True if the 2D histogram on Z-axis is normalized.
        s_label (string, optional): Label for the dataset used for sorting (in max/min modes).
        s_type (string, optional): Sort type, e.g., "min" or "max".
        s_transf_expr (string, optional): Python expression string for transforming sorting data.
        w_label (string, optional): Label for the dataset used as weights.
        w_transf_expr (string, optional): Python expression string for transforming weights data.
        capped_z (bool, optional): True if Z-axis data has been capped.
        capped_label (string, optional): Label describing which data was capped (e.g., "z-axis").
        cap_val (float, optional): The value at which data was capped.
        filter_names (list of strings, optional): Names of datasets used as filters.
        mode_name (string, optional): Name of the plot mode (e.g., "hist1d", "graph2d").
        left_padding (string, optional): String used for indenting info lines.
            Defaults to `defaults.left_padding + " "`.

    Returns:
        list of strings: A list where each string is a formatted line of the info text.
                         The list starts and ends with a padding line.
    """

    # Initialize list to hold all info lines. Start with a padding line.
    info_lines = []
    info_lines.append(left_padding)

    # X-axis information
    line = left_padding + "x-axis: {}".format(x_label)
    info_lines.append(line)
    if x_transf_expr != "": # Add transformation expression if provided.
        line = left_padding + "  - transf.: {}".format(x_transf_expr)
        info_lines.append(line)
    if x_bin_width is not None: # Add bin width if provided (histograms).
        line = left_padding + "  - bin width: {}".format(ff.format(x_bin_width))
        info_lines.append(line)
    if x_range is not None: # Add range information.
        line = left_padding + "  - range: [{}, {}]".format(ff.format(x_range[0]),
                                             ff.format(x_range[1]))
        info_lines.append(line)

    # Y-axis information (if y_label is provided)
    if y_label is not None:
        line = left_padding + "y-axis: {}".format(y_label)
        info_lines.append(line)
        if y_transf_expr != "": # Add Y-axis transformation.
            line = left_padding + "  - transf.: {}".format(y_transf_expr)
            info_lines.append(line)
        if y_normalized_hist: # Indicate if Y-axis histogram is normalized.
            line = left_padding + "  - normalized"
            info_lines.append(line)
        if y_bin_width is not None: # Add Y-axis bin width.
            line = left_padding + "  - bin width: {}".format(ff.format(y_bin_width))
            info_lines.append(line)
        if y_range is not None: # Add Y-axis range.
            line = left_padding + "  - range: [{}, {}]".format(ff.format(y_range[0]),
                                                     ff.format(y_range[1]))
            info_lines.append(line)

    # Z-axis information (if z_label is provided)
    if z_label is not None:
        line = left_padding + "z-axis: {}".format(z_label)
        info_lines.append(line)
        if z_transf_expr != "": # Add Z-axis transformation.
            line = left_padding + "  - transf.: {}".format(z_transf_expr)
            info_lines.append(line)
        if z_normalized_hist: # Indicate if Z-axis histogram is normalized.
            line = left_padding + "  - normalized"
            info_lines.append(line)
        if z_range is not None: # Add Z-axis range.
            line = left_padding + "  - range: [{}, {}]".format(ff.format(z_range[0]),
                                                     ff.format(z_range[1]))
            info_lines.append(line)

    # Sorting information (if s_label and s_type are provided)
    if (s_label is not None) and (s_type is not None):
        line = left_padding + "sort: {} [{}]".format(s_label, s_type)
        info_lines.append(line)
        if s_transf_expr != "": # Add sorting data transformation.
            line = left_padding + "  - transf.: {}".format(s_transf_expr)
            info_lines.append(line)

    # Weights information (if w_label is provided)
    if w_label is not None:
        line = left_padding + "weights: {}".format(w_label)
        info_lines.append(line)
        if w_transf_expr != "": # Add weights data transformation.
            line = left_padding + "  - transf.: {}".format(w_transf_expr)
            info_lines.append(line)

    # Capping information (if capped_z is True)
    if capped_z:
        line = left_padding + "capped: {} dataset capped at {}".format(capped_label,
                                                             ff.format(cap_val))
        info_lines.append(line)

    # Filter information (loop through all filter_names)
    for f_name in filter_names:
        line = left_padding + "filter: {}".format(f_name)
        info_lines.append(line)

    # Plot mode information (if mode_name is provided)
    if mode_name is not None:
        info_lines.append(left_padding) # Add a padding line before mode info.
        line = left_padding + "plot type: {}".format(mode_name)
        info_lines.append(line)

    # Add a final padding line at the end of the info block.
    info_lines.append(left_padding)

    return info_lines




def add_info_text(plot_lines, fig_width, fg_ccode, bg_ccode, **kwargs):
    """Add info text below the plot.

    Args:
        plot_lines (list of strings): The collection of lines.

        fig_width (int): The width of the figure.

        fg_ccode (int): Forground color code.

        bg_ccode (int): Background color code.

        **kwargs: Collection of keyword arguments passed on to the function
            utils.generate_info_text.

    Returns:
        plot_lines (list of strings): The new collection of lines.

        fig_width (int): The new width of the figure.

    """

    info_lines = generate_info_text(**kwargs) 

    for i,line in enumerate(info_lines):
        pretty_line = prettify(line + "  ", fg_ccode, bg_ccode, bold=False)
        plot_lines, fig_width = insert_line(pretty_line, len(line),
                                            plot_lines, fig_width, 
                                            fg_ccode, bg_ccode)

    return plot_lines, fig_width



def get_dataset_names_hdf5(hdf5_file_object):
    """Get the names of all datasets in an HDF5 file.

    Args:
        hdf5_file_object (h5py.File): The HDF5 file.

    Returns:
        result (list of strings): The dataset names.

    """

    import h5py
    result = []
    def get_datasets(name, obj):
        if type(obj) is h5py._hl.dataset.Dataset:
            result.append(name)

    hdf5_file_object.visititems(get_datasets)

    return result



def get_dataset_names_txt(txt_file_name):
    """Get the names of all datasets in a text file.

    Args:
        txt_file_name (string): Path to the input text file. 

    Returns:
        result (list of strings): The dataset names.

    """

    result = []

    # To avoid reading the entire file just to list the dataset names
    # we'll use a StringIO file-like object constructed from the first
    # interesting line in the file.

    comments = '#'

    # Let's find the first non-empty comment line, which we require 
    # should contain the column names.
    # This function assumes that the first non-empty line starting with
    # the comment character '#' contains the dataset names (header).
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
        # If the firstline does not start with the comment character,
        # it might be a data line or a malformed header.
        # We'll try to infer column count if it's not empty.
        if not firstline:
            raise SupRuntimeError(
                f"{error_prefix} Could not find a valid header line (non-empty, starting with '{comments}') "
                f"in file {txt_file_name}. The first non-empty line found was empty or missing."
            )
        n_cols = len(firstline.replace(',', ' ').split())
        if n_cols == 0:
            raise SupRuntimeError(
                f"{error_prefix} Could not parse column names from the first non-empty line in {txt_file_name}. "
                f"The line was: '{firstline}'. It does not start with '{comments}' and no columns could be inferred."
            )
        use_names = ['dataset' + str(i) for i in range(n_cols)]
    elif not firstline.lstrip(comments).strip():
        # The line starts with a comment but is empty otherwise.
        raise SupRuntimeError(
            f"{error_prefix} The header line (starting with '{comments}') in file {txt_file_name} "
            f"is empty after stripping the comment character and whitespace: '{firstline}'"
        )


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



def check_dset_indices(input_file, dset_indices, all_dset_names):
    """Check that the requested datasets were found in the input file

    Args:
        input_file (string): The input file path.

        dset_indices (list of ints): The dataset indices given by the user.

        all_dset_names (list of strings): Names of all datasets found in the
            input file.

    """

    n_sets = len(all_dset_names)

    for dset_index in dset_indices:
        if dset_index >= n_sets:
            raise SupRuntimeError(
                "Cannot use dataset index {}. Valid dataset indices for the "
                "file {} are 0 to {}.".format(dset_index, input_file, n_sets-1)
            )



def check_dset_lengths(dsets, dset_names):
    """Check that the given datasets are of equal length.

    Args:
        dsets (list of numpy.arrays): The datasets to check.

        dset_names (list of strings): The dataset names.

    """

    dset0_length = len(dsets[0])
    for i, dset in enumerate(dsets):
        if len(dset) != dset0_length:
            raise SupRuntimeError(
                "Detected datasets of different lenght. The dataset {} has "
                "length {} while the dataset {} has length {}.".format(
                    dset_names[0], dset0_length, dset_names[i], len(dsets[i]))
            )



def read_input_file(input_file, dset_indices, read_slice, delimiter=' '):
    """Read datasets from an input file.

    The input file can either be of text or HDF5 type. 

    Args:
        input_file (string): The input file path.

        dset_indices (list of ints): The dataset indices given by the user.

        read_slice (slice): The slice to be read for each dataset in use.

        delimiter (string): The delimiter string that separates two entries 
            in the input file, if it's a text file. 

    Returns:
        dsets (list of numpy.arrays): The read datasets.

        dset_names (list of strings): The dataset names.

    """

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

    check_dset_lengths(dsets, dset_names)

    return dsets, dset_names    




def read_input_file_hdf5(input_file, dset_indices, read_slice):
    """Read datasets from an input HDF5 file.

    Args:
        input_file (string): The input HDF5 file path.

        dset_indices (list of ints): The dataset indices given by the user.

        read_slice (slice): The slice to be read for each dataset in use.

    Returns:
        dsets (list of numpy.arrays): The read datasets.

        dset_names (list of strings): The dataset names.

    """

    import h5py
    dsets = []
    dset_names = []

    f = h5py.File(input_file, "r")

    all_dset_names = get_dataset_names_hdf5(f)

    if len(all_dset_names) == 0:
        raise SupRuntimeError("No datasets found in {}.".format(input_file))

    check_dset_indices(input_file, dset_indices, all_dset_names)

    dset_names = [all_dset_names[dset_index] for dset_index in dset_indices]

    try:
        dsets = [np.array(f[dset_name])[read_slice] for dset_name in dset_names]
    except Exception as e:
        print("{} Encountered an unexpected problem when reading the "
              " input file {}. Perhaps there are values missing in the file? "
              "Full error message below.".format(error_prefix, input_file))
        print()
        raise e

    f.close()

    return dsets, dset_names    




def read_input_file_txt(input_file, dset_indices, read_slice, delimiter):
    """Read datasets from an input text file.

    Args:
        input_file (string): The input text file path.

        dset_indices (list of ints): The dataset indices given by the user.

        read_slice (slice): The slice to be read for each dataset in use.

        delimiter (string): The delimiter string that separates two entries 
            in the input file.

    Returns:
        dsets (list of numpy.arrays): The read datasets.

        dset_names (list of strings): The dataset names.

    """

    dsets = []
    dset_names = []

    all_dset_names = get_dataset_names_txt(input_file)

    if len(all_dset_names) == 0:
        raise SupRuntimeError("No datasets found in {}.".format(input_file))

    check_dset_indices(input_file, dset_indices, all_dset_names)
    
    dset_names = [all_dset_names[dset_index] for dset_index in dset_indices]
    
    if delimiter.strip() == "":
        delimiter = None

    try:
        dsets = list(np.genfromtxt(input_file, usecols=dset_indices,
                                    names=dset_names, unpack=True, comments="#", 
                                    delimiter=delimiter))
    except ValueError as e:
        print("{} Encountered an unexpected problem when reading the "
              "input file {}. Perhaps there are values missing in the file? "
              "Full error message below.".format(error_prefix, input_file))
        print()
        raise e

    if len(dset_indices) == 1:
        dsets = [dsets]

    return dsets, dset_names    




def get_filters(input_file, filter_indices, read_slice, delimiter=' '):
    """Get datasets that will be used for filtering (masking).

    The input file can either be of text or HDF5 type. 

    Args:
        input_file (string): The input file path.

        filter_indices (list of ints): The filter dataset indices.

        read_slice (slice): The slice to be read for each dataset in use.

        delimiter (string): The delimiter string that separates two entries 
            in the input file, if it is a text file.

    Returns:
        filter_dsets (list of numpy.arrays): The read filter datasets.

        filter_names (list of strings): The filter dataset names.

    """

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

    check_dset_lengths(filter_dsets, filter_names)

    return filter_dsets, filter_names



def get_filters_hdf5(input_file, filter_indices, read_slice=slice(0,-1,1)):
    """Get HDF5 datasets that will be used for filtering (masking).

    Args:
        input_file (string): The input HDF5 file path.

        filter_indices (list of ints): The filter dataset indices.

        read_slice (slice): The slice to be read for each dataset in use.

    Returns:
        filter_dsets (list of numpy.arrays): The read filter datasets.

        filter_names (list of strings): The filter dataset names.

    """

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
    """Get text-file datasets that will be used for filtering (masking).

    Args:
        input_file (string): The input text file path.

        filter_indices (list of ints): The filter dataset indices.

        read_slice (slice): The slice to be read for each dataset in use.

        delimiter (string): The delimiter string that separates two entries 
            in the input file.

    Returns:
        filter_dsets (list of numpy.arrays): The read filter datasets.

        filter_names (list of strings): The filter dataset names.

    """

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
    """Apply filters (masks) to datasets.

    Args:
        datasets (list of numpy.arrays): The datasets to be filtered.

        filters (list of numpy.arrays): The datasets used as filters.

    Returns:
        filtered_datasets (list of numpy.arrays): The datasets after filtering.

    """

    joint_filter = np.array([np.all(l) for l in zip(*filters)], dtype=np.bool)

    filtered_datasets = []
    for dset in datasets:
        if len(dset) != len(joint_filter):
            raise SupRuntimeError(
                "Attempted to apply a combined filter dataset of length {} to "
                "a dataset of length {}.".format(len(joint_filter), len(dset))
            )

        filtered_datasets.append(dset[joint_filter])

    if len(filtered_datasets[0]) == 0:
        raise SupRuntimeError("No data points left after applying filters.")

    return filtered_datasets




def get_bin_tuples_maxmin_1d(x_data, y_data, xy_bins, x_range, y_range, s_data,
                             s_type, fill_below=False, fill_z_val=-1, 
                             split_marker=False, return_function_data=False,
                             fill_y_val=np.nan):

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



def add_axes(lines, fig_width, xy_bins, x_bin_limits, y_bin_limits, ccs,
             floatf="{: .1e}", add_y_grid_lines=False, add_blank_top_line=True):
    """Adds formatted X and Y axes, ticks, and labels to a list of plot lines.

    This function takes a list of strings (each representing a line of a text-based plot)
    and modifies it by appending axis lines, tick marks, and numerical labels.
    It calculates appropriate tick positions and formats them based on provided limits
    and a float formatting string.

    Args:
        lines (list of strings): The existing plot lines (rows of the plot).
            This list will be modified in-place by prepending/appending axis elements.
        fig_width (int): The current width of the figure. This might be used for
            alignment but the function primarily calculates its own required widths.
        xy_bins (tuple of int): A tuple (x_bins, y_bins) representing the number
            of bins in the x and y dimensions of the plot grid.
        x_bin_limits (numpy.ndarray): An array of values representing the boundaries
            of the x-bins. Used for labeling x-axis ticks.
        y_bin_limits (numpy.ndarray): An array of values representing the boundaries
            of the y-bins. Used for labeling y-axis ticks.
        ccs (CCodeSettings): Color code settings object. Must have attributes like
            `fg_ccode` (foreground), `bg_ccode` (background), and
            `empty_bin_ccode` (for grid lines/alternative ticks).
        floatf (string, optional): Format string for float numbers on axis labels.
            Defaults to "{: .1e}".
        add_y_grid_lines (bool, optional): If True, adds horizontal grid lines
            at y-tick positions. Defaults to False.
        add_blank_top_line (bool, optional): Though present in signature, this
            argument is not directly used in the current implementation logic for
            adding a blank top line (a top line is added regardless).

    Returns:
        tuple:
            - lines (list of strings): The modified list of plot lines including axes.
            - fig_width (int): The original fig_width is returned. Note that
              this function does not recalculate or update fig_width based on
              added axes labels that might extend beyond the original width.
    """

    # mod_func is a helper to apply standard foreground/background color and bold style.
    mod_func = lambda input_str : prettify(input_str, ccs.fg_ccode,
                                           ccs.bg_ccode, bold=True)
    # mod_func_2 is for elements like grid lines, using 'empty_bin_ccode'.
    mod_func_2 = lambda input_str : prettify(input_str, ccs.empty_bin_ccode,
                                             ccs.bg_ccode, bold=True)

    # Determine X-axis tick positions.
    # Aim for a reasonable number of ticks that are not too crowded.
    x_tick_indicies = []
    tick_spacing = 0
    # tick_width is the character width of a formatted number, used for spacing.
    tick_width = len("{}".format(floatf.format(0.0)))
    for n_ticks in range(2,100): # Try increasing number of ticks.
        new_indicies = [
            int(i) for i in np.floor(np.linspace(0, xy_bins[0], n_ticks))
        ]
        # Calculate spacing between ticks in terms of characters (2 chars per bin).
        tick_spacing = (new_indicies[1] - new_indicies[0]) * 2
        if tick_spacing < tick_width + 1:
            break
        x_tick_indicies = new_indicies
    n_x_ticks = len(x_tick_indicies)

    # Determine Y-axis tick positions.
    # Similar logic to x-axis, trying to balance clarity and number of ticks.
    # max_y_ticks aims for roughly one tick every other y-bin.
    max_y_ticks = int(np.ceil(xy_bins[1] / 2.))
    # min_y_ticks ensures a minimum number of y-ticks for very tall plots.
    min_y_ticks = int(np.floor(xy_bins[1] / 10.) + 3)
    yx_bins_ratio = float(xy_bins[1]) / xy_bins[0]
    # Scale number of y-ticks based on x-ticks and aspect ratio.
    n_y_ticks = min(max_y_ticks, int(np.ceil(n_x_ticks * yx_bins_ratio)))
    n_y_ticks = max(n_y_ticks, min_y_ticks) # Ensure minimum number of y-ticks.
    y_tick_indicies = [
        int(i) for i in np.floor(np.linspace(0, xy_bins[1], n_y_ticks))
    ]

    # Reverse y_tick_indicies because plot lines are typically indexed
    # from top (highest y-value or y-bin index) to bottom.
    y_tick_indicies = y_tick_indicies[::-1]


    # Add axis lines to the plot.
    # Prepend a top border line for the plot area.
    top_line = mod_func(" " + "  " * xy_bins[0] + "_")
    lines = [top_line] + lines
    # Add vertical line segments for the Y-axis and tick marks.
    for i in range(len(lines)):
        if i == 0: # Skip the very top border line.
            continue
        if i in y_tick_indicies: # If this line corresponds to a Y-tick index.
            lines[i] = lines[i] + mod_func("│\u0332") # Add tick mark "│̲".
        else:
            lines[i] += mod_func("│") # Add plain axis line segment "│".

    # Construct the X-axis line with tick marks.
    x_axis = " " # Initial padding for x-axis.
    for i in range(n_x_ticks):
        if i == 0: # First tick.
            x_axis += "┼─"
        elif i == (n_x_ticks-1): # Last tick.
            x_axis += "┼"
            break
        else: # Intermediate ticks.
            x_axis += "┼─"
        # Calculate number of dashes "─" needed to reach the next tick.
        bin_diff = x_tick_indicies[i+1] - x_tick_indicies[i]
        x_axis += "─" * (bin_diff * 2 - 2) # 2 chars per bin, minus existing "┼─".
    x_axis = mod_func(x_axis) # Apply formatting
    lines.append(x_axis) # Append the x-axis line to the plot.

    #
    # Add x and y tick labels
    #

    # Prepare Y-tick labels.
    y_tick_labels = []
    for i in y_tick_indicies:
        # y_bin_limits are typically ascending, [::-1] reverses for top-down plot.
        label = "{}".format(floatf.format(y_bin_limits[::-1][i]))
        y_tick_labels.append(label)

    # Add Y-tick labels to the lines, and optional grid lines.
    if add_y_grid_lines:
        for i, tick_index in enumerate(y_tick_indicies):
            # If it's the tick for the top-most data line (last in y_tick_indicies due to reverse).
            if tick_index == y_tick_indicies[-1]: # This was y_tick_indicies[0] before reversal of y_tick_indicies, now it's the "bottom" of y-axis visually
                new_line = mod_func_2(" " + " _" * xy_bins[0]) + mod_func("_")
                lines[tick_index] = new_line
            else:
                # Replace empty bin markers with grid line segments.
                new_line = lines[tick_index].replace("  ", mod_func_2(" _"))
                lines[tick_index] = new_line

            # Append the Y-tick label.
            lines[tick_index] += mod_func("" + y_tick_labels[i] + "   ") # Add padding after label.
    else: # No grid lines, just add labels.
        for i, tick_index in enumerate(y_tick_indicies):
            lines[tick_index] += mod_func("" + y_tick_labels[i] + "   ")

    # Ensure all lines have consistent padding on the right for labels,
    # even if they don't have a Y-tick label themselves.
    for i,line in enumerate(lines):
        if i in y_tick_indicies: # Already handled if it's a tick line.
            pass
        else: # Add padding to align with labeled lines.
            lines[i] += mod_func("" + " "*tick_width + "   ")

    # Prepare X-tick labels.
    x_tick_labels = []
    for i in x_tick_indicies:
        label = "{}".format(floatf.format(x_bin_limits[i]))
        x_tick_labels.append(label)
    x_ticks_line = ""
    for i in range(n_x_ticks):
        tick_label = x_tick_labels[i]
        x_ticks_line += tick_label
        if i == (n_x_ticks-1): # Last label.
            break
        # Calculate spacing to the next label.
        bin_diff = x_tick_indicies[i+1] - x_tick_indicies[i]
        # (bin_diff * 2) is char width to next tick mark. Subtract label length for space.
        x_ticks_line += " " * ((bin_diff * 2) - len(tick_label))

    x_ticks_line = mod_func(x_ticks_line + "     ") # Apply formatting and add trailing padding.
    lines.append(x_ticks_line) # Append the X-tick labels line.

    return lines, fig_width



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



def fill_plot(xy_bins, bins_info, x_bin_limits, y_bin_limits, ccs, ms, 
              get_ccode_and_marker, ff, add_y_grid_lines=True):

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

    plot_width = xy_bins[0] * 2

    # Total figure width
    fig_width = plot_width + 5 + len(ff.format(0))

    # Add axes
    plot_lines, fig_width = add_axes(plot_lines, fig_width, xy_bins, 
                                     x_bin_limits, y_bin_limits, ccs, 
                                     floatf=ff, 
                                     add_y_grid_lines=add_y_grid_lines)

    # Add blank top line
    plot_lines, fig_width = insert_line("", 0, plot_lines, fig_width, 
                                        ccs.fg_ccode, ccs.bg_ccode, 
                                        insert_pos=0)

    return plot_lines, fig_width
