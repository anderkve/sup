# -*- coding: utf-8 -*-
"""
Jules: This module contains helper functions for refactoring sup run modes
to reduce code duplication.
"""

import sup.defaults as defaults
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings
import numpy as np
import sup.utils as utils
# Add other common imports like numpy, utils, colors as needed by helper functions

def setup_common_settings(args, mode_type="1d_generic"):
    """
    Jules: Sets up common CCodeSettings, MarkerSettings, and format strings.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.
    mode_type : str, optional
        Indicates the general type of mode ("1d_generic", "2d_generic", "1d_hist", "2d_hist", etc.)
        to allow for some base customization of markers or colors if needed.
        (Currently, this parameter is illustrative and might not be fully used
         by all modes initially, but provides a hook for future differentiation).

    Returns
    -------
    ccs : CCodeSettings
        Configured CCodeSettings object.
    ms : MarkerSettings
        Configured MarkerSettings object.
    ff : str
        Float format string (e.g., "{: .2e}").
    ff2 : str
        Alternative float format string (e.g., "{:.2e}").
    """
    ccs = CCodeSettings()
    ms = MarkerSettings()

    # Common defaults that might be overridden by specific modes later if needed
    # For 1D modes
    if "1d" in mode_type:
        ccs.graph_ccodes["grayscale_bb"] = 231  # Black on white fg
        ccs.graph_ccodes["grayscale_wb"] = 232  # White on black fg
        ccs.graph_ccodes["color_bb"] = 4 # Blue on black bg
        ccs.graph_ccodes["color_wb"] = 12 # Blue on white bg for 1D
        ms.empty_bin_marker = defaults.empty_bin_marker_1d
        if "hist" in mode_type or "post1d" in mode_type: # Specific for histograms/posteriors
            ms.regular_marker_up = " █"
            ms.regular_marker_down = " ▄"
            ms.fill_marker = " █"

    # For 2D modes (colormap based)
    elif "2d" in mode_type:
        if hasattr(args, 'cmap_index') and args.cmap_index is not None:
            import sup.colors as colors # Import only if needed
            ccs.cmaps["color_bb"] = colors.cmaps[args.cmap_index]
            ccs.cmaps["color_wb"] = colors.cmaps[args.cmap_index]
        if hasattr(args, 'n_colors') and args.n_colors is not None:
            ccs.use_n_colors = args.n_colors
        ms.empty_bin_marker = defaults.empty_bin_marker_2d

    # General settings from args
    if hasattr(args, 'use_white_bg'):
        ccs.use_white_bg = args.use_white_bg
    if hasattr(args, 'use_grayscale'):
        ccs.use_grayscale = args.use_grayscale
    
    ccs.update() # Apply settings

    if "2d" in mode_type and hasattr(args, 'reverse_colormap') and args.reverse_colormap:
        ccs.ccodes = ccs.ccodes[::-1]

    n_decimals = defaults.n_decimals
    if hasattr(args, 'n_decimals') and args.n_decimals is not None:
        n_decimals = args.n_decimals
    
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"

    return ccs, ms, ff, ff2

def read_and_transform_data(args, dset_definitions):
    """
    Jules: Reads data from file, applies filters, and evaluates transformations.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments. Must contain attributes like:
        `input_file`, `read_slice`, `delimiter`, `filter_indices`,
        and transformation expressions (e.g., `x_transf_expr`, `y_transf_expr`).
    dset_definitions : collections.OrderedDict
        An OrderedDict where keys are logical dataset names (e.g., 'x', 'y', 'z', 'w', 's', 'loglike')
        and values are the corresponding user-provided indices (e.g., `args.x_index`, `args.w_index`).
        The order determines the order in the `utils.read_input_file` call.
        If an index is None (e.g., optional weight not provided), it should be handled.

    Returns
    -------
    processed_data : dict
        A dictionary containing:
        - '{name}_data': numpy.ndarray for each dataset (e.g., 'x_data', 'y_data').
        - '{name}_name': str for each dataset name from file (e.g., 'x_name', 'y_name').
        - 'filter_names': list of str, names of applied filters.
        - Original transformation expressions can also be included if useful for info text.
    """
    input_file = args.input_file
    read_slice = slice(*args.read_slice)
    delimiter = args.delimiter
    filter_indices = args.filter_indices

    # Prepare lists for reading data
    indices_to_read = []
    logical_names_for_indices = []
    for name, index_val in dset_definitions.items():
        if index_val is not None:
            indices_to_read.append(index_val)
            logical_names_for_indices.append(name)

    raw_dsets, raw_dset_names = utils.read_input_file(
        input_file,
        indices_to_read,
        read_slice,
        delimiter=delimiter
    )

    # Store raw data and names in a dictionary based on logical_names_for_indices
    current_data = {}
    # Ensure raw_dsets is a list, even if only one dataset is returned
    if not isinstance(raw_dsets, list):
        raw_dsets = [raw_dsets]

    for i, name_key in enumerate(logical_names_for_indices):
        current_data[f"{name_key}_data"] = raw_dsets[i]
        current_data[f"{name_key}_name"] = raw_dset_names[i]

    # Handle optional datasets not read from file (e.g., default weights)
    if 'w' in dset_definitions and dset_definitions['w'] is None:
        if 'x_data' in current_data: 
            current_data['w_data'] = np.ones(len(current_data['x_data']))
            # Ensure w_name is also set, even if to a default or None
            current_data['w_name'] = getattr(args, 'w_name', "default_weights")


    # Filters
    filter_datasets, filter_names_from_util = utils.get_filters(
        input_file,
        filter_indices,
        read_slice=read_slice,
        delimiter=delimiter
    )
    current_data['filter_names'] = filter_names_from_util

    if filter_indices: 
        datasets_to_filter_keys = [] 
        original_datasets_list = []

        # Use the order from dset_definitions to ensure consistency
        for name_key in dset_definitions.keys(): 
            data_key = f"{name_key}_data"
            if data_key in current_data: 
                datasets_to_filter_keys.append(data_key)
                original_datasets_list.append(current_data[data_key])
        
        if original_datasets_list: 
            filtered_dsets_list = utils.apply_filters(original_datasets_list, filter_datasets)
            if not isinstance(filtered_dsets_list, list): # Ensure list for single dataset
                filtered_dsets_list = [filtered_dsets_list]
            for i, key_to_update in enumerate(datasets_to_filter_keys):
                current_data[key_to_update] = filtered_dsets_list[i]


    # Transformations
    eval_context = {"np": np}
    for name_key in dset_definitions.keys():
        data_key = f"{name_key}_data"
        if data_key in current_data:
             eval_context[name_key] = current_data[data_key] 

    # Second pass for transformations, ensuring data is in context before transforming
    for name_key in dset_definitions.keys():
        data_key = f"{name_key}_data"
        transf_expr_key = f"{name_key}_transf_expr" 
        
        if hasattr(args, transf_expr_key):
            expression = getattr(args, transf_expr_key)
            # Store expression regardless of whether data exists, for info text
            if expression:
                 current_data[transf_expr_key] = expression

            if expression and data_key in current_data: 
                current_data[data_key] = eval(expression, {"np": np}, eval_context)
                eval_context[name_key] = current_data[data_key] # Update context

    # Check for specific dataset requirements, e.g., weights
    if 'w_data' in current_data : # Check if weights were processed
         w_name_to_check = current_data.get('w_name', "") # Get w_name if it exists
         utils.check_weights(current_data['w_data'], w_name_to_check)

    return current_data

# Jules: More helper functions will be added below.
