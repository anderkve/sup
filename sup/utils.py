# -*- coding: utf-8 -*-
import os
import sys
import io
import numpy as np
from collections import OrderedDict
from scipy.stats import chi2
# from io import StringIO # Replaced by io.StringIO
import sup.defaults as defaults


error_prefix = "sup error:"

class SupRuntimeError(Exception):
    """Exceptions class for sup runtime errors"""
    pass



def prettify(input_string, fg_ccode, bg_ccode, bold=True, reset=True):
    """Add pretty formatting for the input string.

    Parameters
    ----------
    input_string : str
        The input string.
    fg_ccode : int
        Foreground color code.
    bg_ccode : int
        Background color code.
    bold : bool, optional
        Use bold text? Defaults to True.
    reset : bool, optional
        Reset format at the end of the string? Defaults to True.

    Returns
    -------
    str
        The formatted string.

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

    Parameters
    ----------
    new_line : str
        The new line.
    new_line_width : int
        The length of the new line without any formatting.
    old_lines_list : list of str
        The collection of existing lines.
    old_width : int
        Length of the longest (unformatted) existing line.
    fg_ccode : int
        Foreground color code.
    bg_ccode : int
        Background color code.
    insert_pos : int, optional
        List index where new_line should be inserted. Defaults to None, which
        appends the line to the end of the list.

    Returns
    -------
    tuple
        A tuple containing:
            - result_lines_list (list of str): The new collection of lines.
            - result_width (int): The new width of the longest line.

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

    Parameters
    ----------
    plot_lines : list of str
        The collection of lines.
    fg_ccode : int
        Foreground color code.
    bg_ccode : int
        Background color code.
    left_padding : int, optional
        The number of spaces to add. Defaults to `defaults.left_padding`.

    Returns
    -------
    list of str
        The new collection of lines with left padding added.

    """

    for i,line in enumerate(plot_lines):
        plot_lines[i] = prettify(left_padding, fg_ccode, bg_ccode) + line

    return plot_lines



def generate_legend(legend_entries, bg_ccode, sep="  ", internal_sep=" ",
                    left_padding=" "):
    """Generate a plot legend line.

    Parameters
    ----------
    legend_entries : list of tuple
        A list with one tuple for each entry in the legend. Each tuple
        is of the form (marker, marker_ccode, txt, txt_ccode).
        - marker (str): The marker string.
        - marker_ccode (int): Foreground color code for the marker.
        - txt (str): The text label for the legend entry.
        - txt_ccode (int): Foreground color code for the text.
    bg_ccode : int
        Background color code.
    sep : str, optional
        String used to separate legend entries. Defaults to "  ".
    internal_sep : str, optional
        String used to separate the marker and the text in a legend entry.
        Defaults to " ".
    left_padding : str, optional
        Whitespace string used for left padding. Defaults to " ".

    Returns
    -------
    tuple
        A tuple containing:
            - legend (str): The constructed legend line.
            - legend_width (int): The width of the legend line (unformatted length).

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



def generate_colorbar(plot_lines, fig_width, ff, ccs, color_z_lims, 
                      extend_up=False, extend_down=False):
    """Generate a color bar and add it to the plot_lines.

    This function constructs a color bar legend, including the color
    swatches and corresponding numerical labels, and appends it to the
    existing plot lines. It also adjusts the figure width if the
    colorbar is wider than the current figure.

    Parameters
    ----------
    plot_lines : list of str
        The collection of lines representing the plot onto which the colorbar
        will be added. Each string is a line of the plot.
    fig_width : int
        The current width of the figure (in characters). This may be updated
        if the colorbar is wider.
    ff : str
        Format string for floats used to format the numerical labels on the
        colorbar (e.g., "{:.2f}").
    ccs : CCodeSettings
        An object or dictionary containing color code settings, specifically:
        - ccs.ccodes (list of int): A list of color codes for the color swatches.
        - ccs.fg_ccode (int): The foreground color code for text and non-swatch elements.
        - ccs.bg_ccode (int): The background color code for the plot area.
        - ccs.empty_bin_ccode (int): Color code for elements like separators if needed.
    color_z_lims : list of float
        A list of float values representing the boundaries for each color in
        the color bar. These are the numerical values that will be labeled
        on the colorbar.
    extend_up : bool
        Add right arrow after the rightmost colorswatch.
    extend_up : bool
        Add left arrow before the leftmost colorswatch.

    Returns
    -------
    tuple
        A tuple containing:
            - plot_lines (list of str): The updated collection of lines with the
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

        # Start the colorbar with a left arrow?
        if (i == 0) and (extend_down):
            cb_entries.append(("◀", ccodes[i], "", fg_ccode))

        # Add a color swatch (■■■■■■) and its preceding separator (|).
        # The last limit doesn't get a swatch after it, just a final separator.
        if i < (n_color_lims - 1):
            cb_entries.append(("|", bar_ccode, 6*"■", ccodes[i])) # Separator, then color swatch.
        else:
            if extend_up:
                cb_entries.append(("|", bar_ccode, "▶", ccodes[n_color_lims - 2]))
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
    if extend_down:
        cb_nums_entries.append(("  ", fg_ccode, "", fg_ccode))
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

    Parameters
    ----------
    ff : str, optional
        Format string for floating-point numbers. Defaults to `defaults.ff2`.
    x_label : str, optional
        Label for the X-axis.
    x_range : tuple of float, optional
        Min and max values for the X-axis range.
    x_bin_width : float, optional
        Width of bins along the X-axis (for histograms).
    y_label : str, optional
        Label for the Y-axis.
    y_range : tuple of float, optional
        Min and max values for the Y-axis range.
    y_bin_width : float, optional
        Width of bins along the Y-axis (for histograms).
    z_label : str, optional
        Label for the Z-axis (e.g., for 2D histograms or color values).
    z_range : tuple of float, optional
        Min and max values for the Z-axis range.
    x_transf_expr : str, optional
        Python expression string used to transform X-axis data. Defaults to "".
    y_transf_expr : str, optional
        Python expression string used to transform Y-axis data. Defaults to "".
    z_transf_expr : str, optional
        Python expression string used to transform Z-axis data. Defaults to "".
    y_normalized_hist : bool, optional
        True if the 1D histogram on Y-axis is normalized. Defaults to False.
    z_normalized_hist : bool, optional
        True if the 2D histogram on Z-axis is normalized. Defaults to False.
    s_label : str, optional
        Label for the dataset used for sorting (in max/min modes).
    s_type : str, optional
        Sort type, e.g., "min" or "max".
    s_transf_expr : str, optional
        Python expression string for transforming sorting data. Defaults to "".
    w_label : str, optional
        Label for the dataset used as weights.
    w_transf_expr : str, optional
        Python expression string for transforming weights data. Defaults to "".
    capped_z : bool, optional
        True if Z-axis data has been capped. Defaults to False.
    capped_label : str, optional
        Label describing which data was capped (e.g., "z-axis"). Defaults to "z-axis".
    cap_val : float, optional
        The value at which data was capped. Defaults to 1e99.
    filter_names : list of str, optional
        Names of datasets used as filters. Defaults to an empty list.
    mode_name : str, optional
        Name of the plot mode (e.g., "hist1d", "graph2d").
    left_padding : str, optional
        String used for indenting info lines.
        Defaults to `defaults.left_padding + " "`.

    Returns
    -------
    list of str
        A list where each string is a formatted line of the info text.
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

    Parameters
    ----------
    plot_lines : list of str
        The collection of lines.
    fig_width : int
        The width of the figure.
    fg_ccode : int
        Foreground color code.
    bg_ccode : int
        Background color code.
    **kwargs
        Collection of keyword arguments passed on to the function
        `utils.generate_info_text`.

    Returns
    -------
    tuple
        A tuple containing:
            - plot_lines (list of str): The new collection of lines.
            - fig_width (int): The new width of the figure.

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

    Parameters
    ----------
    hdf5_file_object : h5py.File
        The HDF5 file object.

    Returns
    -------
    list of str
        The dataset names.

    """

    import h5py
    result = []
    def get_datasets(name, obj):
        """Callback function for h5py.File.visititems to find datasets.

        This function is designed to be used as a callable for the
        `visititems` method of an `h5py.File` object. It checks if the
        visited HDF5 item `obj` is a dataset. If it is, the item's
        `name` is appended to the `result` list, which is defined in
        the enclosing scope of `get_dataset_names_hdf5`.

        This function relies on the `result` list from the outer scope
        and the `h5py` library.

        Args:
            name (str): The name of the HDF5 item being visited.
            obj (h5py.HLObject): The HDF5 item object itself.
                Expected to be an instance of `h5py._hl.dataset.Dataset`
                if it's a dataset.

        Returns:
            None: This function modifies the `result` list in place.
        """
        if type(obj) is h5py._hl.dataset.Dataset:
            result.append(name)

    hdf5_file_object.visititems(get_datasets)

    return result



def get_dataset_names_txt(source):
    """Get the names of all datasets in a text file or stream.

    The function assumes that the first non-empty line starting with the
    comment character '#' contains the dataset names (header). If no such
    line is found, or if the line is malformed, it attempts to infer column
    names as "dataset0", "dataset1", etc., based on the first data line.

    Parameters
    ----------
    source : str or file-like object
        Path to the input text file or a file-like object (e.g., sys.stdin).

    Returns
    -------
    tuple
        A tuple containing:
            - result_names (list of str): The parsed dataset names.
            - file_content (str): The full string content of the file or stdin.

    Raises
    ------
    SupRuntimeError
        If a valid header line cannot be found and column names cannot be
        inferred, or if the header line is empty after stripping comments
        and whitespace.

    """

    result = []

    file_content = ""
    if isinstance(source, str):
        with open(source, 'r') as f:
            file_content = f.read()
        display_source_name = source
    else: # assume file-like object for stdin
        file_content = source.read()
        display_source_name = "stdin"

    comments = '#'
    header_line_str = ''
    lines = file_content.splitlines()
    
    for line in lines:
        stripped_line = line.lstrip().rstrip()
        if not ((stripped_line == '') or (stripped_line == comments)):
            header_line_str = stripped_line
            break # Found the first relevant line

    use_names = True
    # If header_line_str is not a comment header with column names, 
    # we have to create a list of names based on the number of columns 
    # we detect from header_line_str.
    if not header_line_str.startswith(comments):
        if not header_line_str: # Empty or only whitespace after reading all lines
            raise SupRuntimeError(
                f"{error_prefix} Could not find a valid header line (non-empty, starting with '{comments}') "
                f"or any data lines in {display_source_name}."
            )
        # Assume it's a data line, try to infer column count
        # Replace comma with space for robust splitting, then split by whitespace
        n_cols = len(header_line_str.replace(',', ' ').split())
        if n_cols == 0:
            raise SupRuntimeError(
                f"{error_prefix} Could not parse column names from the first non-empty line in {display_source_name}. "
                f"The line was: '{header_line_str}'. It does not start with '{comments}' and no columns could be inferred."
            )
        result_names = ['dataset' + str(i) for i in range(n_cols)]
    else: # Starts with comment character
        # Check if the line is empty after stripping comment char and whitespace
        actual_header_content = header_line_str.lstrip(comments).strip()
        if not actual_header_content:
            raise SupRuntimeError(
                f"{error_prefix} The header line (starting with '{comments}') in {display_source_name} "
                f"is empty after stripping the comment character and whitespace: '{header_line_str}'"
            )
        # Use np.genfromtxt on this single header line to get names
        # Pass actual_header_content directly to StringIO
        stringIO_header = io.StringIO(actual_header_content)
        try:
            # We pass names=True to auto-detect names from this line.
            # delimiter=None will split by whitespace. If names are comma-separated, this will treat them as one.
            # This part of np.genfromtxt is primarily for data, but can extract names.
            # A more robust way would be to split actual_header_content by delimiter if known,
            # but this function's original logic used genfromtxt.
            # Forcing delimiter to None (whitespace) for header parsing is safer.
            dset_dtype = np.genfromtxt(stringIO_header, names=True, comments=None, max_rows=1, delimiter=None).dtype
            result_names = list(dset_dtype.names)
            if not result_names: # If genfromtxt failed to parse names (e.g. bad format)
                 raise ValueError("genfromtxt failed to parse names from header.")
        except Exception as e: # Catch broad exceptions from genfromtxt if header is tricky
            # Fallback: simple split by whitespace (and comma as a common alternative)
            cleaned_header = actual_header_content.replace(',', ' ')
            result_names = [name for name in cleaned_header.split() if name]
            if not result_names:
                 raise SupRuntimeError(
                    f"{error_prefix} Failed to parse column names from header line '{header_line_str}' in {display_source_name} using genfromtxt and fallback split. Error: {e}"
                )
    
    return result_names, file_content


def read_input_file_txt_from_stream_content(file_content_str, all_dset_names, dset_indices, read_slice, delimiter):
    """Read datasets from a string containing text file content.

    Parameters
    ----------
    file_content_str : str
        The full content of the text file as a string.
    all_dset_names : list of str
        Names of all datasets found in the input file content.
    dset_indices : list of int
        The dataset column indices (0-based) to read.
    read_slice : slice
        The slice to be applied to each read dataset.
    delimiter : str
        The delimiter string that separates entries.

    Returns
    -------
    tuple
        A tuple containing:
            - dsets (list of numpy.ndarray): The list of read datasets.
            - dset_names (list of str): The list of names for the read datasets.
    """
    dset_names = [all_dset_names[dset_index] for dset_index in dset_indices]

    if delimiter.strip() == "":
        delimiter = None

    data_stream = io.StringIO(file_content_str)
    
    try:
        # Read all columns specified by dset_indices. names=None as we handle names based on all_dset_names.
        # np.genfromtxt will return a structured array if multiple columns, or a single array if one column.
        loaded_data = np.genfromtxt(data_stream, usecols=dset_indices, names=None, comments="#", 
                                    delimiter=delimiter, unpack=False) # unpack=False to handle single column case better initially
    except ValueError as e:
        print("{} Encountered an unexpected problem when reading from stream. "
              "Perhaps there are values missing? Full error message below.".format(error_prefix))
        print()
        raise e

    # Ensure dsets is a list of arrays, even if only one dataset is read
    if len(dset_indices) == 1:
        # If loaded_data is 1D, it's a single column. If it's >1D (e.g. structured), something else is wrong.
        # For a single column, genfromtxt (unpack=False) returns a 1D array.
        if loaded_data.ndim == 1:
            dsets = [loaded_data[read_slice]]
        else: # Should not happen with names=None and single usecol.
             raise SupRuntimeError("Unexpected data shape when reading a single column from stream.")
    else:
        # If multiple columns are read with names=None and unpack=False, 
        # genfromtxt returns a structured array. We need to convert it to a list of arrays.
        # This is different from unpack=True which returns a list of arrays directly.
        # Let's re-evaluate using unpack=True for consistency.
        # Re-trying with unpack=True as it's more direct for multiple columns.
        data_stream.seek(0) # Reset stream for re-read
        dsets_tuple = np.genfromtxt(data_stream, usecols=dset_indices, names=None, comments="#", 
                                   delimiter=delimiter, unpack=True)
        if len(dset_indices) == 1: # unpack=True still returns single array not in tuple if one col
             dsets = [dsets_tuple[read_slice]]
        else:
             dsets = [d[read_slice] for d in dsets_tuple]


    return dsets, dset_names


def check_file_type(input_file):
    """Determine file type based on file extension.

    Parameters
    ----------
    input_file : str
        The input file path.

    Returns
    -------
    str
        The identified file type. Can be "text" or "hdf5".

    """

    # Default assumption is that the input file is a text file.
    file_type = "text"

    filename_without_extension, file_extension = os.path.splitext(input_file)    

    if file_extension in ['.hdf5', '.h5', '.he5']:
        file_type = "hdf5"

    return file_type



def check_dset_indices(input_file, dset_indices, all_dset_names):
    """Check that the requested datasets were found in the input file.

    Parameters
    ----------
    input_file : str
        The input file path.
    dset_indices : list of int
        The dataset indices given by the user.
    all_dset_names : list of str
        Names of all datasets found in the input file.

    Raises
    ------
    SupRuntimeError
        If any dataset index in `dset_indices` is out of bounds for
        `all_dset_names`.

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

    Parameters
    ----------
    dsets : list of numpy.ndarray
        The datasets to check.
    dset_names : list of str
        The dataset names, corresponding to `dsets`.

    Raises
    ------
    SupRuntimeError
        If datasets in `dsets` have different lengths.

    """

    dset0_length = len(dsets[0])
    for i, dset in enumerate(dsets):
        if len(dset) != dset0_length:
            raise SupRuntimeError(
                "Detected datasets of different lenght. The dataset {} has "
                "length {} while the dataset {} has length {}.".format(
                    dset_names[0], dset0_length, dset_names[i], len(dsets[i]))
            )



def read_input_file(input_file_path_or_stream, dset_indices, read_slice, delimiter=' ', stdin_format=None):
    """Read datasets from an input file or stream.

    The input can be a file path (str) or a file-like object (e.g., sys.stdin).
    The type is determined by `check_file_type` for files, or `stdin_format` for streams.

    Parameters
    ----------
    input_file_path_or_stream : str or file-like object
        The input file path or stream.
    dset_indices : list of int
        The dataset indices to read.
    read_slice : slice
        The slice to be read for each dataset.
    delimiter : str, optional
        The delimiter for text files. Defaults to ' '.
    stdin_format : str, optional
        Format of stdin ('txt', 'csv'), required if reading from stdin. Defaults to None.

    Returns
    -------
    tuple
        A tuple containing:
            - dsets (list of numpy.ndarray): The read datasets.
            - dset_names (list of str): The names of the read datasets.

    Raises
    ------
    SupRuntimeError
        If issues occur during file reading or dataset validation (e.g.,
        datasets have different lengths).

    """

    dsets = []
    dset_names = []

    # Check if input_file_path_or_stream is sys.stdin or a similar stream object
    # A simple check for '-' is used if sup.py translates it to sys.stdin later,
    # or we can check type if sys.stdin is passed directly.
    # For this refactoring, we'll assume sup.py might pass sys.stdin directly,
    # or a string '-' which it resolves. The task description mentions input_file == '-'
    # in sup.py. Let's assume if it's not a string, it's a stream (like sys.stdin).
    
    is_stream_input = not isinstance(input_file_path_or_stream, str) or input_file_path_or_stream == '-'

    if is_stream_input:
        # If it's '-', assume it means sys.stdin should be used by the caller.
        # Here, we expect the actual stream object if '-' was resolved by caller.
        # If '-' is passed, it implies caller needs to handle it. Let's refine this logic
        # based on assumption that if input_file_path_or_stream is not a string path, it's a stream.
        # The problem states `sup.py` uses `input_file == '-'`.
        # `read_input_file` in `utils.py` will receive `sys.stdin` if `input_file` was `'-'`.
        
        actual_stream = sys.stdin if input_file_path_or_stream == '-' else input_file_path_or_stream

        if not stdin_format:
            raise SupRuntimeError("stdin_format must be specified when reading from a stream.")

        print("Reading from stdin as {}...".format(stdin_format))
        print() # for spacing, similar to file reading messages

        if stdin_format == 'txt':
            all_dset_names, file_content_str = get_dataset_names_txt(actual_stream)
            check_dset_indices("stdin", dset_indices, all_dset_names)
            dsets, dset_names = read_input_file_txt_from_stream_content(
                file_content_str, all_dset_names, dset_indices, read_slice, delimiter
            )
        elif stdin_format == 'csv':
            all_dset_names, file_content_str = get_dataset_names_csv(actual_stream)
            check_dset_indices("stdin", dset_indices, all_dset_names)
            dsets, dset_names = read_input_file_csv_from_stream_content(
                file_content_str, all_dset_names, dset_indices, read_slice
            )
        elif stdin_format == 'hdf5':
            raise SupRuntimeError("HDF5 from stdin is not supported.")
        else:
            raise SupRuntimeError("Unknown stdin format: {}".format(stdin_format))
    else:
        # It's a filename string
        file_type = check_file_type(input_file_path_or_stream)

        if file_type == "text":
            print("Reading " + input_file_path_or_stream + " as a text file with delimiter '" +
                  delimiter + "'")
            print()
            dsets, dset_names = read_input_file_txt(input_file_path_or_stream, dset_indices,
                                                    read_slice, delimiter)
        elif file_type == "hdf5":
            print("Reading " + input_file_path_or_stream + " as an HDF5 file")
            print()
            dsets, dset_names = read_input_file_hdf5(input_file_path_or_stream, dset_indices,
                                                     read_slice)
        else:
            # Should not happen if check_file_type is robust
            raise SupRuntimeError("Unknown file type for: {}".format(input_file_path_or_stream))

    check_dset_lengths(dsets, dset_names)
    return dsets, dset_names




def read_input_file_hdf5(input_file, dset_indices, read_slice):
    """Read datasets from an input HDF5 file.

    Parameters
    ----------
    input_file : str
        The input HDF5 file path.
    dset_indices : list of int
        The dataset indices (0-based) to read from the HDF5 file.
    read_slice : slice
        The slice to apply when reading each dataset.

    Returns
    -------
    tuple
        A tuple containing:
            - dsets (list of numpy.ndarray): The list of read datasets.
            - dset_names (list of str): The list of names for the read datasets.

    Raises
    ------
    SupRuntimeError
        If no datasets are found in the file, if a dataset index is invalid,
        or if an unexpected error occurs during reading.
    Exception
        Propagates exceptions from `h5py` if dataset reading fails.

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




def read_input_file_txt(txt_file_name, dset_indices, read_slice, delimiter):
    """Read datasets from an input text file.

    Parameters
    ----------
    txt_file_name : str
        The input text file path.
    dset_indices : list of int
        The dataset column indices (0-based) to read from the text file.
    read_slice : slice
        The slice to be read for each dataset.
    delimiter : str
        The delimiter string that separates entries in the input file.
        If `delimiter` consists only of whitespace, it is treated as `None`
        by `np.genfromtxt` to handle whitespace-separated values correctly.

    Returns
    -------
    tuple
        A tuple containing:
            - dsets (list of numpy.ndarray): The list of read datasets.
            - dset_names (list of str): The list of names for the read datasets.

    Raises
    ------
    SupRuntimeError
        If no datasets (columns) are found in the file, if a dataset index
        is invalid, or if `np.genfromtxt` encounters a `ValueError` (e.g.,
        due to missing values or malformed data).
    ValueError
        Propagates `ValueError` from `np.genfromtxt` if data conversion issues occur.

    """

    all_dset_names, file_content_str = get_dataset_names_txt(txt_file_name)

    if len(all_dset_names) == 0: # Should ideally be caught by get_dataset_names_txt
        raise SupRuntimeError("No datasets found in {}.".format(txt_file_name))

    check_dset_indices(txt_file_name, dset_indices, all_dset_names)
    
    return read_input_file_txt_from_stream_content(file_content_str, all_dset_names, dset_indices, read_slice, delimiter)


def get_dataset_names_csv(source):
    """Get the names of all datasets in a CSV file or stream.

    The function assumes that the first line contains the dataset names (header).

    Parameters
    ----------
    source : str or file-like object
        Path to the input CSV file or a file-like object (e.g., sys.stdin).

    Returns
    -------
    tuple
        A tuple containing:
            - result_names (list of str): The parsed dataset names.
            - file_content (str): The full string content of the file or stdin.
    """
    file_content_str = ""
    if isinstance(source, str):
        with open(source, 'r') as f:
            file_content_str = f.read()
        display_source_name = source
    else: # assume file-like object for stdin
        file_content_str = source.read()
        display_source_name = "stdin"

    if not file_content_str.strip():
        raise SupRuntimeError(f"{error_prefix} The input from {display_source_name} is empty.")

    header_line_str = file_content_str.splitlines()[0]

    if not header_line_str.strip():
        raise SupRuntimeError(f"{error_prefix} The header line in {display_source_name} is empty.")

    try:
        # Use np.genfromtxt on this single header line to get names.
        # Set comments to None as CSVs don't typically have comment lines like text files.
        # delimiter is explicitly ','.
        stringIO_header = io.StringIO(header_line_str)
        # Setting invalid_raise=False for genfromtxt when parsing header, as it might be too strict.
        dset_dtype = np.genfromtxt(stringIO_header, delimiter=',', names=True, comments=None, max_rows=1, invalid_raise=False).dtype
        result_names = list(dset_dtype.names)
        if not result_names: # If genfromtxt failed (e.g. all names were invalid according to its rules)
             # Fallback: simple split by comma, strip quotes and spaces
             result_names = [name.strip().strip('"').strip("'") for name in header_line_str.split(',') if name.strip()]
             if not result_names:
                 raise ValueError("genfromtxt and fallback failed to parse names from CSV header.")
    except Exception as e:
        # Fallback: simple split by comma, strip quotes and spaces
        result_names = [name.strip().strip('"').strip("'") for name in header_line_str.split(',') if name.strip()]
        if not result_names:
            raise SupRuntimeError(
                f"{error_prefix} Failed to parse column names from CSV header line '{header_line_str}' in {display_source_name} using genfromtxt and fallback split. Error: {e}"
            )
            
    return result_names, file_content_str


def read_input_file_csv_from_stream_content(file_content_str, all_dset_names, dset_indices, read_slice):
    """Read datasets from a string containing CSV file content.

    Parameters
    ----------
    file_content_str : str
        The full content of the CSV file as a string.
    all_dset_names : list of str
        Names of all datasets found in the input file content (typically from header).
    dset_indices : list of int
        The dataset column indices (0-based) to read.
    read_slice : slice
        The slice to be applied to each read dataset.

    Returns
    -------
    tuple
        A tuple containing:
            - dsets (list of numpy.ndarray): The list of read datasets.
            - dset_names (list of str): The list of names for the read datasets.
    """
    dset_names = [all_dset_names[dset_index] for dset_index in dset_indices]
    data_stream = io.StringIO(file_content_str)

    try:
        # Use names=True to skip header, comments=None as CSVs don't usually have them.
        # unpack=True is important to get columns as separate arrays.
        dsets_tuple = np.genfromtxt(data_stream, usecols=dset_indices, delimiter=',', 
                                    names=True, comments=None, unpack=True, invalid_raise=False)
                                    # names=True tells genfromtxt to use the first line as header and skip it for data.
                                    # Using names=None and then manually skipping header might be another option if names=True is problematic.
                                    # However, the get_dataset_names_csv already parsed the header, so we want to skip it.
                                    # A common way to skip header with genfromtxt is skip_header=1 if names are handled manually.
                                    # Let's re-evaluate: since all_dset_names are already parsed, we should skip the header row.
    except ValueError as e:
        print("{} Encountered an unexpected problem when reading CSV from stream. "
              "Full error message below.".format(error_prefix))
        print()
        raise e

    # Reset stream and read again, this time skipping the header.
    # This is safer as `names=True` might have subtle effects on type or data reading.
    data_stream.seek(0)
    try:
        # We use usecols to select specific columns.
        # unpack=True ensures that dsets_tuple is a tuple of arrays, one for each column.
        # skip_header=1 to ignore the CSV header line.
        dsets_tuple_data = np.genfromtxt(data_stream, usecols=dset_indices, delimiter=',', 
                                         skip_header=1, comments=None, unpack=True)
    except ValueError as e:
        # This error might occur if, after skipping header, data is still problematic
        print("{} Encountered an unexpected problem when reading CSV data (post-header) from stream. "
              "Full error message below.".format(error_prefix))
        print()
        raise e

    if len(dset_indices) == 1:
        # If only one column is selected, np.genfromtxt (with unpack=True) returns a single 1D array, not a tuple.
        dsets = [dsets_tuple_data[read_slice]]
    else:
        # If multiple columns, it returns a tuple of 1D arrays.
        dsets = [d[read_slice] for d in dsets_tuple_data]

    return dsets, dset_names


def get_filters_txt_from_stream_content(file_content_str, all_dset_names, filter_indices, read_slice, delimiter):
    """Get text-file datasets from a string that will be used for filtering (masking)."""
    filter_names = [all_dset_names[filter_index] for filter_index in filter_indices]
    
    if delimiter.strip() == "":
        delimiter = None

    data_stream = io.StringIO(file_content_str)
    # skip_header=1 assumes that the header was part of file_content_str and needs to be skipped for data reading.
    # This aligns with how read_input_file_txt_from_stream_content implicitly handles it via get_dataset_names_txt.
    filter_dsets_tuple = np.genfromtxt(data_stream, usecols=filter_indices, names=None, comments="#", 
                                   delimiter=delimiter, unpack=True, skip_header=1)

    if len(filter_indices) == 1:
        filter_dsets = [filter_dsets_tuple[read_slice]]
    else:
        filter_dsets = [d[read_slice] for d in filter_dsets_tuple]
        
    return filter_dsets, filter_names


def get_filters_csv_from_stream_content(file_content_str, all_dset_names, filter_indices, read_slice):
    """Get CSV datasets from a string that will be used for filtering (masking)."""
    filter_names = [all_dset_names[filter_index] for filter_index in filter_indices]
    data_stream = io.StringIO(file_content_str)
    
    # For CSV, delimiter is ',', comments=None, skip_header=1
    filter_dsets_tuple = np.genfromtxt(data_stream, usecols=filter_indices, delimiter=',', 
                                   names=None, comments=None, unpack=True, skip_header=1)

    if len(filter_indices) == 1:
        filter_dsets = [filter_dsets_tuple[read_slice]]
    else:
        filter_dsets = [d[read_slice] for d in filter_dsets_tuple]
        
    return filter_dsets, filter_names


def get_filters(input_file_path_or_stream, filter_indices, read_slice, delimiter=' ', stdin_format=None):
    """Get datasets that will be used for filtering (masking) from file or stream.

    Parameters
    ----------
    input_file_path_or_stream : str or file-like object
        The path to the input file or a stream.
    filter_indices : list of int or None
        A list of integer indices specifying which datasets to read as filters.
        If None, returns empty lists for datasets and names.
    read_slice : slice
        A slice object indicating the portion of each dataset to read.
    delimiter : str, optional
        The delimiter used in the input file if it's a text file. Defaults to ' '.
    stdin_format : str, optional
        Format of stdin ('txt', 'csv'), required if reading from stdin. Defaults to None.
    
    Returns
    -------
    tuple
        A tuple containing:
            - filter_dsets (list of numpy.ndarray): Filter datasets.
            - filter_names (list of str): Names of filter datasets.

    Raises
    ------
    SupRuntimeError
        If `check_dset_lengths` fails, indicating filter datasets have
        inconsistent lengths.

    """

    if filter_indices is None:
        return [], []

    filter_dsets = []
    filter_names = []
    
    is_stream_input = not isinstance(input_file_path_or_stream, str) or input_file_path_or_stream == '-'

    if is_stream_input:
        actual_stream = sys.stdin if input_file_path_or_stream == '-' else input_file_path_or_stream
        
        if not stdin_format:
            raise SupRuntimeError("stdin_format must be specified when reading filters from a stream.")

        print("Reading filters from stdin as {}...".format(stdin_format)) # User feedback
        
        if stdin_format == 'txt':
            all_dset_names, file_content_str = get_dataset_names_txt(actual_stream)
            check_dset_indices("stdin (for filters)", filter_indices, all_dset_names)
            filter_dsets, filter_names = get_filters_txt_from_stream_content(
                file_content_str, all_dset_names, filter_indices, read_slice, delimiter
            )
        elif stdin_format == 'csv':
            all_dset_names, file_content_str = get_dataset_names_csv(actual_stream)
            check_dset_indices("stdin (for filters)", filter_indices, all_dset_names)
            filter_dsets, filter_names = get_filters_csv_from_stream_content(
                file_content_str, all_dset_names, filter_indices, read_slice
            )
        elif stdin_format == 'hdf5':
            raise SupRuntimeError("HDF5 filters from stdin are not supported.")
        else:
            raise SupRuntimeError("Unknown stdin format for filters: {}".format(stdin_format))
    else:
        # It's a filename string
        file_type = check_file_type(input_file_path_or_stream)
        
        if file_type == "text":
            # get_filters_txt was refactored to handle reading content and calling _from_stream_content
            # It also means check_dset_indices is implicitly handled by the call to get_dataset_names_txt within get_filters_txt
            # However, for consistency and explicit message, we might want to call check_dset_indices here too
            # Let's assume get_filters_txt calls get_dataset_names_txt which returns all_names,
            # then get_filters_txt calls check_dset_indices itself, or it's done here.
            # The refactored get_filters_txt ALREADY calls get_dataset_names_txt.
            # It does NOT call check_dset_indices. So we should call it here.
            # To do that, get_filters_txt needs to return all_dset_names or we parse again.
            # For now, let's simplify: get_filters_txt will directly return dsets and names.
            # The internal call to get_dataset_names_txt inside get_filters_txt will ensure names are valid before reading.
            # The check_dset_indices for the *specific filter_indices* should be done here.
            # This requires get_filters_txt to also return all_dset_names.
            # Alternative: get_dataset_names_txt once, then pass content for filters.
            # Let's adjust get_filters_txt to NOT call get_dataset_names_txt, but receive content.
            # This seems more aligned with the overall strategy.
            # Re-evaluating: The current `get_filters_txt` *does* call `get_dataset_names_txt`.
            # This means `check_dset_indices` against `all_dset_names` should be done in `get_filters_txt`
            # or `get_filters_txt` should return `all_dset_names` for this function to do it.
            # The current `get_filters_txt` does:
            #    all_dset_names, file_content_str = get_dataset_names_txt(txt_file_name)
            #    return get_filters_txt_from_stream_content(...)
            # So, `all_dset_names` is available. Let's pass it back or do check inside.
            # For simplicity, let's assume get_filters_txt handles this check internally or check_dset_indices is called by caller after.
            # The prompt for get_filters_txt did not include check_dset_indices.
            # Let's add it here for file paths.
            print("Reading filters from text file {}...".format(input_file_path_or_stream))
            all_dset_names_for_file, _ = get_dataset_names_txt(input_file_path_or_stream) # Get names for check
            check_dset_indices(input_file_path_or_stream, filter_indices, all_dset_names_for_file)
            filter_dsets, filter_names = get_filters_txt(input_file_path_or_stream, # This will re-read names, inefficient.
                                                         filter_indices,
                                                         read_slice,
                                                         delimiter)
        elif file_type == "hdf5":
            print("Reading filters from HDF5 file {}...".format(input_file_path_or_stream))
            # get_filters_hdf5 reads directly from file path, no stream intermediary for names needed here.
            # It should internally call get_dataset_names_hdf5 and check_dset_indices.
            # Let's verify get_filters_hdf5 structure:
            #   f = h5py.File(input_file, "r")
            #   dset_names = get_dataset_names_hdf5(f)
            #   ... then it iterates filter_indices and appends. It implicitly checks index validity.
            filter_dsets, filter_names = get_filters_hdf5(input_file_path_or_stream, 
                                                          filter_indices, 
                                                          read_slice)
        else:
            raise SupRuntimeError("Unknown file type for filters: {}".format(input_file_path_or_stream))

    if filter_dsets: # Only check lengths if datasets were actually loaded
        check_dset_lengths(filter_dsets, filter_names)

    return filter_dsets, filter_names



def get_filters_hdf5(input_file, filter_indices, read_slice=slice(0,-1,1)): # Renaming for clarity in get_filters
    """Get HDF5 datasets that will be used for filtering (masking).

    Parameters
    ----------
    input_file : str
        The path to the input HDF5 file.
    filter_indices : list of int or None
        A list of integer indices specifying which datasets to read as filters.
        If None, the function will still open the HDF5 file to get all dataset
        names but will return empty lists for filter datasets and names if
        `filter_indices` itself is None (though the current implementation
        implies `filter_indices` would not be None if this function is directly called
        with the intent to load filters).
    read_slice : slice, optional
        A slice object indicating the portion of each dataset to read.
        Defaults to `slice(0, -1, 1)`, which typically means all elements
        except the last (this might be an unintentional default depending on
        use case, common full slice is `slice(None)` or `[:]`).

    Returns
    -------
    tuple
        A tuple containing:
            - filter_dsets (list of numpy.ndarray): A list of NumPy arrays,
              where each array is a filter dataset.
            - filter_names (list of str): A list of names for the filter datasets.

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



def get_filters_txt(txt_file_name, filter_indices, read_slice, delimiter=' '):
    """Get text-file datasets that will be used for filtering (masking).

    Parameters
    ----------
    txt_file_name : str
        The path to the input text file.
    filter_indices : list of int
        A list of integer indices specifying which columns (datasets) to read
        as filters.
    read_slice : slice
        A slice object indicating the portion of each dataset to read.
    delimiter : str, optional
        The delimiter used in the input text file. Defaults to ' '.

    Returns
    -------
    tuple
        A tuple containing:
            - filter_dsets (list of numpy.ndarray): A list of NumPy arrays.
            - filter_names (list of str): A list of names for the filter datasets.
    """
    all_dset_names, file_content_str = get_dataset_names_txt(txt_file_name)
    if not all_dset_names: 
        raise SupRuntimeError(f"No dataset names found in {txt_file_name} while trying to get filters.")
    # check_dset_indices is deferred to the main get_filters function
    return get_filters_txt_from_stream_content(file_content_str, all_dset_names, filter_indices, read_slice, delimiter)



def apply_filters(datasets, filters):
    """Apply filters (masks) to datasets.

    Parameters
    ----------
    datasets : list of numpy.ndarray
        The list of datasets (NumPy arrays) to be filtered.
    filters : list of numpy.ndarray
        The list of filter datasets (NumPy arrays of boolean type or
        convertible to boolean). Each filter in this list is combined
        with an AND operation to create a joint filter.

    Returns
    -------
    list of numpy.ndarray
        The list of datasets after applying the combined filter.

    Raises
    ------
    SupRuntimeError
        If a dataset and the joint filter have different lengths, or if
        applying filters results in an empty dataset.

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
    """Determine representative (x,y,z) tuples for 1D data based on max/min sorting.

    For each x-bin, this function identifies the y-value corresponding to the
    maximum or minimum value in `s_data` within that x-bin. This is used for
    visualizing a 1D function or profile where a selection criterion (max/min
    of `s_data`) determines which y-value to plot.

    Parameters
    ----------
    x_data : numpy.ndarray
        The x-coordinates of the data points.
    y_data : numpy.ndarray
        The y-coordinates of the data points.
    xy_bins : tuple of int
        A tuple (x_bins, y_bins) specifying the number of bins along the
        x and y axes.
    x_range : tuple of float
        A tuple (x_min, x_max) specifying the range of the x-axis.
    y_range : tuple of float
        A tuple (y_min, y_max) specifying the range of the y-axis.
    s_data : numpy.ndarray
        The data array used for sorting to select the representative y-value
        in each x-bin. Must have the same length as `x_data` and `y_data`.
    s_type : {"min", "max"}
        The sorting type. "max" selects the y-value where `s_data` is maximal
        within the x-bin, "min" selects where `s_data` is minimal.
    fill_below : bool, optional
        If True, bins below the selected (x,y) point are filled with `fill_z_val`.
        Defaults to False.
    fill_z_val : int, optional
        The value used to fill bins below the selected point if `fill_below` is True.
        Typically represents a special marker or color index. Defaults to -1.
    split_marker : bool, optional
        If True, the z-value in the output tuple is adjusted based on whether
        the selected y-value is above or below the y-bin center. This can be
        used to select different plot markers. Defaults to False.
    return_function_data : bool, optional
        If True, additionally returns the processed x and y data arrays that
        represent the selected function line. Defaults to False.
    fill_y_val : float, optional
        The value to assign to y-data in x-bins where no data points exist.
        Defaults to `np.nan`.

    Returns
    -------
    result_dict : collections.OrderedDict
        An ordered dictionary where keys are (x_bin_index, y_bin_index) tuples
        and values are (x_bin_center, y_bin_center, z_value) tuples.
        The z_value is typically 1, or adjusted by `split_marker` or `fill_below`.
    x_bin_limits : numpy.ndarray
        The calculated bin limits for the x-axis.
    y_bin_limits : numpy.ndarray
        The calculated bin limits for the y-axis.
    new_xdata : numpy.ndarray, optional
        The x-coordinates of the selected function line. Only returned if
        `return_function_data` is True.
    new_ydata : numpy.ndarray, optional
        The y-coordinates of the selected function line. Only returned if
        `return_function_data` is True.

    Notes
    -----
    - Assumes `x_data` and `y_data` (and `s_data`) are of equal length.
    - `np.digitize` is used for binning, so care should be taken with edge cases
      and `right=True` for y-binning.
    """
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
    """Determine representative (x,y,z) tuples based on max/min sorting of s_data.

    For each (x,y) bin, this function identifies the z-value and original data
    index corresponding to the maximum or minimum value in `s_data` within
    that bin. This is useful for visualizing 2D data where a third dimension
    (`s_data`) dictates which point to represent in each bin.

    Parameters
    ----------
    x_data : numpy.ndarray
        The x-coordinates of the data points.
    y_data : numpy.ndarray
        The y-coordinates of the data points.
    z_data : numpy.ndarray
        The z-values associated with each (x,y) point.
    xy_bins : tuple of int
        A tuple (x_bins, y_bins) specifying the number of bins along the
        x and y axes.
    x_range : tuple of float
        A tuple (x_min, x_max) specifying the range of the x-axis.
    y_range : tuple of float
        A tuple (y_min, y_max) specifying the range of the y-axis.
    s_data : numpy.ndarray
        The data array used for sorting to select the representative z-value
        in each (x,y)-bin. Must have the same length as `x_data`, `y_data`,
        and `z_data`.
    s_type : {"min", "max"}
        The sorting type. "max" selects the z-value where `s_data` is maximal
        within the bin, "min" selects where `s_data` is minimal.

    Returns
    -------
    result_dict : collections.OrderedDict
        An ordered dictionary where keys are (x_bin_index, y_bin_index) tuples
        and values are (x_bin_center, y_bin_center, selected_z_value, data_index)
        tuples. `data_index` is the index of the selected point in the original
        input arrays.
    x_bin_limits : numpy.ndarray
        The calculated bin limits for the x-axis.
    y_bin_limits : numpy.ndarray
        The calculated bin limits for the y-axis.

    Notes
    -----
    - Assumes `x_data`, `y_data`, `z_data`, and `s_data` are of equal length.
    - `s_type` must be either "min" or "max".
    - `np.digitize` is used for binning.
    """
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
    """Determine representative (x,y,z) tuples for 1D data based on averaging y-values.

    For each x-bin, this function calculates the average of y-values falling
    into that bin. This is used for visualizing a 1D profile or function
    derived by averaging y-data across x-bins.

    Parameters
    ----------
    x_data : numpy.ndarray
        The x-coordinates of the data points.
    y_data : numpy.ndarray
        The y-coordinates of the data points.
    xy_bins : tuple of int
        A tuple (x_bins, y_bins) specifying the number of bins along the
        x and y axes. `y_bins` is used to digitize the resulting average y-values.
    x_range : tuple of float
        A tuple (x_min, x_max) specifying the range of the x-axis.
    y_range : tuple of float
        A tuple (y_min, y_max) specifying the range of the y-axis for digitizing
        the average y-values.
    fill_below : bool, optional
        If True, bins below the calculated average (x,y) point are filled
        with `fill_z_val`. Defaults to False.
    fill_z_val : int, optional
        The value used to fill bins below the average point if `fill_below` is True.
        Typically represents a special marker or color index. Defaults to -1.
    split_marker : bool, optional
        If True, the z-value in the output tuple is adjusted based on whether
        the average y-value is above or below the y-bin center. This can be
        used to select different plot markers. Defaults to False.

    Returns
    -------
    result_dict : collections.OrderedDict
        An ordered dictionary where keys are (x_bin_index, y_bin_index) tuples
        and values are (x_bin_center, y_bin_center, z_value) tuples.
        The z_value is typically 1, or adjusted by `split_marker` or `fill_below`.
    x_bin_limits : numpy.ndarray
        The calculated bin limits for the x-axis.
    y_bin_limits : numpy.ndarray
        The calculated bin limits for the y-axis.

    Notes
    -----
    - Assumes `x_data` and `y_data` are of equal length.
    - If an x-bin is empty, it does not contribute to `new_xdata` or `new_ydata`
      (the internal averaged arrays), and thus won't appear in `result_dict`
      unless `fill_below` logic adds entries.
    """
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
    """Determine representative (x,y,z) tuples based on averaging z-values.

    For each (x,y) bin, this function calculates the average of z-values
    for all data points falling into that bin. This is useful for creating
    a 2D heatmap or summary plot where the color or marker represents the
    average z-value in each bin.

    Parameters
    ----------
    x_data : numpy.ndarray
        The x-coordinates of the data points.
    y_data : numpy.ndarray
        The y-coordinates of the data points.
    z_data : numpy.ndarray
        The z-values associated with each (x,y) point. These are averaged
        within each bin.
    xy_bins : tuple of int
        A tuple (x_bins, y_bins) specifying the number of bins along the
        x and y axes.
    x_range : tuple of float
        A tuple (x_min, x_max) specifying the range of the x-axis.
    y_range : tuple of float
        A tuple (y_min, y_max) specifying the range of the y-axis.

    Returns
    -------
    result_dict : collections.OrderedDict
        An ordered dictionary where keys are (x_bin_index, y_bin_index) tuples
        and values are (x_bin_center, y_bin_center, average_z_value) tuples.
        Only bins with at least one data point are included.
    x_bin_limits : numpy.ndarray
        The calculated bin limits for the x-axis.
    y_bin_limits : numpy.ndarray
        The calculated bin limits for the y-axis.

    Notes
    -----
    - Assumes `x_data`, `y_data`, and `z_data` are of equal length.
    - `np.digitize` is used for binning.
    """
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

    Parameters
    ----------
    lines : list of str
        The existing plot lines (rows of the plot). This list will be modified
        by prepending/appending axis elements.
    fig_width : int
        The current width of the figure. This is used for alignment and is
        returned, though not recalculated if labels extend beyond it.
    xy_bins : tuple of int
        A tuple (x_bins, y_bins) representing the number of bins in the x and
        y dimensions of the plot grid.
    x_bin_limits : numpy.ndarray
        An array of values representing the boundaries of the x-bins. Used for
        labeling x-axis ticks.
    y_bin_limits : numpy.ndarray
        An array of values representing the boundaries of the y-bins. Used for
        labeling y-axis ticks.
    ccs : CCodeSettings
        An object or dictionary containing color code settings, specifically:
        - ccs.fg_ccode (int): Foreground color for axis lines and text.
        - ccs.bg_ccode (int): Background color for the plot area.
        - ccs.empty_bin_ccode (int): Color for grid lines or alternate ticks.
    floatf : str, optional
        Format string for float numbers on axis labels. Defaults to "{: .1e}".
    add_y_grid_lines : bool, optional
        If True, adds horizontal grid lines at y-tick positions. Defaults to False.
    add_blank_top_line : bool, optional
        If True, a blank line is added at the top of the plot lines.
        Defaults to True. Note: The current implementation adds a top border line
        regardless of this parameter, but this parameter might be intended for
        an additional truly blank line.

    Returns
    -------
    tuple
        A tuple containing:
            - lines (list of str): The modified list of plot lines including axes.
            - fig_width (int): The original `fig_width`. This function does not
              recalculate or update `fig_width` if added axis labels extend
              beyond this width.
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



def get_cl_included_bins_1d(confidence_levels, y_func_data, dx, chisq=False):
    """Determine which bins are included within specified confidence levels (CL).

    This function is used for 1D profile likelihoods or chi-square functions
    where `y_func_data` represents normalized likelihood values (or L/L_max)
    or delta chi-square values, and the goal is to find regions (sets of bins) 
    corresponding to certain confidence levels.

    Parameters
    ----------
    confidence_levels : list of float
        A list of confidence levels (e.g., [68.0, 95.0]) for which to
        determine the included bins. Values should be percentages (0-100).
    y_func_data : numpy.ndarray
        A 1D array of normalized likelihoods (L/L_max), where the 
        maximum non-NaN value is assumed to be 1.0.
    dx : float
        The width of each bin. While present in the signature, this parameter
        is not used in the current implementation of this function. It might
        be a remnant or intended for future use related to probability density.
    chisq : bool
        If True, the y_func_data is interpreted as delta chi^2 values

    Returns
    -------
    list of list of int
        A list of lists, where each inner list contains the integer indices
        of the bins included for the corresponding confidence level in
        `confidence_levels`.

    Notes
    -----
    - The function assumes that the maximum of `y_func_data` (excluding NaNs) is 1.0.
    - The threshold for including a bin is calculated using the chi-squared
      distribution with one degree of freedom (chi2.ppf(cl_percentage, df=1)),
      transformed to a likelihood ratio threshold: exp(-0.5 * chi2_value).
    - Bins with NaN values in `y_func_data` are excluded.
    """
    included_bins = []

    # Check assumption that the max (non-NaN) y element is 1.0 (for likelihood ratio)
    # or that the min y element is close to 0.0 (for delta chi^2).
    # Using np.nanmax and np.nanmin to handle potential NaNs gracefully
    if chisq:
        min_y_val = np.nanmin(y_func_data)
        if not np.isclose(min_y_val, 0.0):
            assert np.isclose(min_y_val, 0.0), "Min of y_func_data (excluding NaNs) is not close to 0.0"
    else:
        max_y_val = np.nanmax(y_func_data)
        if not np.isclose(max_y_val, 1.0):
            assert np.isclose(max_y_val, 1.0), "Max of y_func_data (excluding NaNs) is not close to 1.0"

    indices = list(range(len(y_func_data)))

    for cl in confidence_levels:

        # Shortcut for 100% region
        if cl >= 100.0:
            included_bins.append(indices)
            continue

        if chisq:
            # Calculate the correct delta chi^2 threshold for the given CL
            pp = cl * 0.01
            chisq_thres = chi2.ppf(pp, df=1)

            inc_bins = []
            for index in indices:
                y_val = y_func_data[index]
                if np.isnan(y_val):
                    continue
                if y_val <= chisq_thres:
                    inc_bins.append(index)
            included_bins.append(inc_bins)
        else:
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
    """Determine which bins are included within specified credible regions (CR).

    This function is typically used for 1D histograms or probability distributions
    where `bins_content` represents the probability or count in each bin.
    It identifies the smallest set of bins whose cumulative probability (or sum
    of content) meets or exceeds each specified credible region percentage,
    starting from the bins with the highest content.

    Parameters
    ----------
    credible_regions : list of float
        A list of credible region percentages (e.g., [68.0, 95.0]) for which
        to determine the included bins. Values should be percentages (0-100).
    bins_content : numpy.ndarray
        A 1D array where each element represents the content (e.g., probability,
        count) of the corresponding bin.
    dx : float
        The width of each bin. This is used to calculate the contribution of
        each bin to the cumulative sum, effectively `bin_content * dx`.
        The sum is then compared against `cr / 100.0` if `bins_content`
        represents a density, or `cr` if `bins_content` is already scaled
        (the current code multiplies by `dx * 100`, so `bins_content` should
        likely be a density for `cr_sum` to be a percentage).

    Returns
    -------
    list of list of int
        A list of lists, where each inner list contains the integer indices
        of the bins included for the corresponding credible region in
        `credible_regions`. The bins are typically sorted by content before
        accumulation.

    Notes
    -----
    - The function sorts bins by their content in descending order.
    - It iteratively adds bins to the included set until the cumulative sum
      (scaled by `dx * 100`) exceeds the target credible region percentage.
    - A refinement step is included to check if adding the current bin makes
      the sum closer to the target CR than not adding it, which helps in
      selecting the most compact region.
    """
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
    """Convert lists of included bin indices into contiguous range(s).

    For each list of bin indices (representing, e.g., a confidence or
    credible region), this function identifies contiguous blocks of bins
    and represents them as (start_index, end_index) for bin indices and
    (start_position, end_position) for actual coordinate values based on
    `bin_limits`.

    Parameters
    ----------
    included_bins : list of list of int
        A list where each inner list contains sorted integer indices of bins
        that are part of a particular region (e.g., a specific CL or CR).
    bin_limits : numpy.ndarray
        A 1D array of bin edge coordinates. `bin_limits[i]` is the lower edge
        of bin `i`, and `bin_limits[i+1]` is the upper edge.

    Returns
    -------
    tuple of (list of list of tuple, list of list of tuple)
        A tuple containing two lists:
        - result_bin_indices (list of list of tuple of int):
          For each input list of included bins, this contains a list of
          (start_bin_index, end_bin_index + 1) tuples representing the
          contiguous ranges of bin indices.
        - result_positions (list of list of tuple of float):
          For each input list of included bins, this contains a list of
          (start_position, end_position) tuples representing the contiguous
          ranges in terms of coordinate values from `bin_limits`.

    Notes
    -----
    - Each inner list in `included_bins` is expected to be sorted in ascending order.
    - The `end_bin_index` in `result_bin_indices` is exclusive (i.e., `range(start, end)`).
    - The `end_position` in `result_positions` corresponds to `bin_limits[end_bin_index + 1]`.
    """
    result_bin_indices = []
    result_positions = []
    for inc_bins_list in included_bins:

        # print("START new CR: inc_bins_list: ", inc_bins_list) # Debugging print
        ranges_bin_indices = []
        ranges_positions = []

        if not inc_bins_list: # Handle empty list of included bins
            result_bin_indices.append(ranges_bin_indices)
            result_positions.append(ranges_positions)
            continue

        inc_bins_list.sort()

        inside = False
        begin_bi = 0
        # end_bi = 0 # Not strictly needed to initialize here
        n_bins = len(inc_bins_list)

        for i, bi in enumerate(inc_bins_list):
            # print("i: ", i, "   bi: ", bi, "  inside: ", inside) # Debugging print
            if not inside:
                begin_bi = bi
                inside = True

            # Check if current bin `bi` is the last in `inc_bins_list` or
            # if the next bin in `inc_bins_list` is not contiguous with `bi`.
            if (i == n_bins - 1) or (inc_bins_list[i+1] != bi + 1):
                end_bi = bi + 1 # Current bin `bi` is the last in this contiguous range.
                                # end_bi is exclusive for range, so bi + 1.
                ranges_bin_indices.append((begin_bi, end_bi))
                ranges_positions.append((bin_limits[begin_bi], bin_limits[end_bi]))
                inside = False
            # If still inside a contiguous range, continue to the next bin.
            # else: # This 'else' is implicit if the 'if' condition above is not met.
                # print(" - found next!") # Debugging print: means inc_bins_list[i+1] == bi + 1

        result_bin_indices.append(ranges_bin_indices)
        result_positions.append(ranges_positions)

    return result_bin_indices, result_positions



def get_bar_str(ranges_pos, bin_limits):
    """Generate a string representation of a bar for confidence/credible regions.

    This function creates a text-based bar string (e.g., "  ├─────┤   ")
    that visually represents one or more contiguous ranges on a binned axis.
    It's used to draw the horizontal bars for confidence or credible intervals
    below a plot.

    Parameters
    ----------
    ranges_pos : list of tuple of float
        A list of tuples, where each tuple `(start_pos, end_pos)` defines
        a contiguous range in terms of coordinate values.
    bin_limits : numpy.ndarray
        A 1D array of bin edge coordinates that define the overall axis.
        Used to determine the bin indices corresponding to `start_pos`
        and `end_pos`.

    Returns
    -------
    str
        A string representing the bar, composed of spaces, and line-drawing
        characters (e.g., '├', '─', '┤', '╶', '╴').
    """
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
    """Generate a list of strings, each representing a credible region bar.

    For each specified credible region percentage, this function calculates
    the included bins (using `get_cr_included_bins_1d` and
    `get_ranges_from_included_bins`), generates a bar string representation
    (using `get_bar_str`), and appends the CR percentage as a label.

    Parameters
    ----------
    credible_regions : list of float
        A list of credible region percentages (e.g., [68.0, 95.0]) for which
        to generate bar strings.
    bins_content : numpy.ndarray
        A 1D array representing the content (e.g., probability mass or density)
        of each bin. Passed to `get_cr_included_bins_1d`.
    bin_limits : numpy.ndarray
        A 1D array of bin edge coordinates. Passed to
        `get_ranges_from_included_bins` and `get_bar_str`.
    ff2 : str
        Format string used for formatting the credible region percentage in the
        label (e.g., "{:.1f}% CR"). Note: The current implementation uses
        "{:.12g}% CR" directly, so `ff2` is effectively unused here.

    Returns
    -------
    list of str
        A list of strings, where each string is a formatted bar representing
        a credible region, complete with a label.
    """
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
                                   bin_limits, ff2, chisq=False):
    """Generate a list of strings, each representing a confidence level bar.

    For each specified confidence level percentage, this function calculates
    the included bins (using `get_cl_included_bins_1d` and
    `get_ranges_from_included_bins`), generates a bar string representation
    (using `get_bar_str`), and appends the CL percentage as a label.

    Parameters
    ----------
    confidence_levels : list of float
        A list of confidence level percentages (e.g., [68.0, 95.0]) for which
        to generate bar strings.
    y_func_data : numpy.ndarray
        A 1D array of y-values, as normalized likelihoods (L/L_max) or 
        delta chi^2 values (if chisq=True)
        Passed to `get_cl_included_bins_1d`.
    bin_limits : numpy.ndarray
        A 1D array of bin edge coordinates. Passed to
        `get_ranges_from_included_bins` and `get_bar_str`.
    ff2 : str
        Format string used for formatting the confidence level percentage in the
        label (e.g., "{:.1f}% CI"). Note: The current implementation uses
        "{:.12g}% CI" directly, so `ff2` is effectively unused here.
    chisq : bool
        If True, the y_func_data is interpreted as delta chi^2 values

    Returns
    -------
    list of str
        A list of strings, where each string is a formatted bar representing
        a confidence level, complete with a label.
    """
    cl_bar_lines = []

    dx = bin_limits[1] - bin_limits[0]

    included_bins = get_cl_included_bins_1d(confidence_levels, y_func_data, dx, chisq=chisq)

    cl_ranges_indices, cl_ranges_pos = \
        get_ranges_from_included_bins(included_bins, bin_limits)

    for cl_index,cl_val in enumerate(confidence_levels):
        
        bar_str = get_bar_str(cl_ranges_pos[cl_index], bin_limits)

        bar_str += "{:.12g}% CI".format(cl_val)

        cl_bar_lines.append(bar_str)

    return cl_bar_lines



def check_weights(w_data, w_name=""):
    """Validate the weights data array.

    Checks if the weights data array `w_data` is valid for use in weighted
    calculations. Specifically, it ensures that no weights are negative and
    that not all weights are zero or less.

    Parameters
    ----------
    w_data : numpy.ndarray
        A NumPy array containing the weights.
    w_name : str, optional
        An optional name for the weights dataset, used in error messages for
        better context. Defaults to "".

    Raises
    ------
    SupRuntimeError
        If `w_data` contains any negative values, or if all values in `w_data`
        are less than or equal to zero.

    Returns
    -------
    None
        This function does not return a value but raises an error if
        validation fails.
    """
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
    """Construct the main plot area, including data points and axes.

    This function generates the lines representing the plot grid, populates it
    with markers based on `bins_info`, and then adds axes, ticks, and labels.

    Parameters
    ----------
    xy_bins : tuple of int
        A tuple (x_bins, y_bins) specifying the number of bins (grid cells)
        in the x and y dimensions.
    bins_info : dict
        A dictionary where keys are (xi, yi) tuples representing bin indices,
        and values contain information needed by `get_ccode_and_marker` to
        determine the marker and color for that bin.
    x_bin_limits : numpy.ndarray
        An array of values representing the boundaries of the x-bins.
        Passed to `add_axes`.
    y_bin_limits : numpy.ndarray
        An array of values representing the boundaries of the y-bins.
        Passed to `add_axes`.
    ccs : CCodeSettings
        An object or dictionary containing color code settings, used for
        empty bins, markers, and axes. Must have attributes like `fg_ccode`,
        `bg_ccode`, `empty_bin_ccode`.
    ms : MarkerSettings
        An object or dictionary containing marker settings, primarily
        `ms.empty_bin_marker` for empty bins.
    get_ccode_and_marker : function
        A callback function `get_ccode_and_marker(bin_key)` that takes a
        bin key `(xi, yi)` and returns a `(ccode, marker)` tuple for that bin.
    ff : str
        Format string for float numbers on axis labels. Passed to `add_axes`.
    add_y_grid_lines : bool, optional
        If True, adds horizontal grid lines at y-tick positions when calling
        `add_axes`. Defaults to True.

    Returns
    -------
    tuple
        A tuple containing:
            - plot_lines (list of str): A list of strings, where each string
              is a fully formatted line of the plot including data and axes.
            - fig_width (int): The calculated width of the figure, including
              plot area and axis labels.
    """
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
