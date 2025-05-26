# -*- coding: utf-8 -*-

"""sup.post2dmode

A sup run mode that produces a 2d joint posterior distribution for 
variables x and y.

"""

import numpy as np
import sup.defaults as defaults
import sup.utils as utils
import sup.colors as colors
from collections import OrderedDict
from sup.ccodesettings import CCodeSettings
from sup.markersettings import MarkerSettings


def run(args):
    """The main function for the 'post2d' run mode.

    This function 
    - interprets the command-line arguments for this run mode;
    - reads and processes the data as appropriate for this run mode;
    - constructs the full output as a list of strings; and
    - prints the output to screen.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    
    """

    input_file = args.input_file

    x_index = args.x_index
    y_index = args.y_index

    w_index = args.w_index
    use_weights = bool(w_index is not None)

    credible_regions = args.credible_regions
    if not credible_regions:
        credible_regions = [68.3, 95.45]
    credible_regions.append(100.0)

    credible_regions = np.array(credible_regions)

    filter_indices = args.filter_indices
    use_filters = bool(filter_indices is not None) 

    x_range = args.x_range
    y_range = args.y_range

    read_slice = slice(*args.read_slice)

    xy_bins = args.xy_bins
    if not xy_bins:
        xy_bins = defaults.xy_bins

    ccs = CCodeSettings()
    ccs.cmaps["color_bb"] = colors.cmaps[args.cmap_index]
    ccs.cmaps["color_wb"] = colors.cmaps[args.cmap_index]
    ccs.use_white_bg = args.use_white_bg
    ccs.use_grayscale = args.use_grayscale
    ccs.use_n_colors = len(credible_regions)
    ccs.update()

    # In posterior mode we use a reversed colormap by default, to assign the
    # "warmest" colour to the first credible region (z_val = region index = 0).
    ccs.ccodes = ccs.ccodes[::-1]

    # The user can still reverse it, though.
    if args.reverse_colormap:
        ccs.ccodes = ccs.ccodes[::-1]

    ms = MarkerSettings()
    ms.empty_bin_marker = defaults.empty_bin_marker_2d

    n_decimals = args.n_decimals
    ff = "{: ." + str(n_decimals) + "e}"
    ff2 = "{:." + str(n_decimals) + "e}"


    #
    # Read datasets from file
    #

    x_name = None
    x_data = None
    y_name = None
    y_data = None
    w_name = None
    w_data = None

    if use_weights:
        dsets, dset_names = utils.read_input_file(args.input_file,
                                                  [x_index, y_index, w_index],
                                                  read_slice,
                                                  delimiter=args.delimiter,
                                                  stdin_format=args.stdin_format)
        x_data, y_data, w_data = dsets
        x_name, y_name, w_name = dset_names
        utils.check_weights(w_data, w_name)
    else:
        dsets, dset_names = utils.read_input_file(args.input_file,
                                                  [x_index, y_index],
                                                  read_slice,
                                                  delimiter=args.delimiter,
                                                  stdin_format=args.stdin_format)
        x_data, y_data = dsets
        x_name, y_name = dset_names
        w_data = np.ones(len(x_data))

    filter_datasets, filter_names = utils.get_filters(args.input_file,
                                                      filter_indices,
                                                      read_slice=read_slice,
                                                      delimiter=args.delimiter,
                                                      stdin_format=args.stdin_format)

    if use_filters:
        x_data, y_data, w_data = utils.apply_filters([x_data, y_data, w_data],
                                                     filter_datasets)

    x_transf_expr = args.x_transf_expr
    y_transf_expr = args.y_transf_expr
    w_transf_expr = args.w_transf_expr
    # @todo: add the x,y,w variables to a dictionary of allowed arguments 
    #        to eval()
    x = x_data
    y = y_data
    w = w_data
    if x_transf_expr != "":
        x_data = eval(x_transf_expr)
    if y_transf_expr != "":
        y_data = eval(y_transf_expr)
    if w_transf_expr != "":
        w_data = eval(w_transf_expr)

    posterior_mean_x = np.average(x_data, weights=w_data)
    posterior_mean_y = np.average(y_data, weights=w_data)

    if not x_range:
        x_range = [np.min(x_data), np.max(x_data)]
    if not y_range:
        y_range = [np.min(y_data), np.max(y_data)]



    #
    # Get a dict with info per bin
    #

    bins_content_unweighted,_ ,_  = np.histogram2d(
        x_data, y_data, bins=xy_bins, range=[x_range, y_range], density=True)
    bins_content, x_bin_limits, y_bin_limits = np.histogram2d(
        x_data, y_data, bins=xy_bins, range=[x_range, y_range], weights=w_data,
        density=True)

    dx = x_bin_limits[1] - x_bin_limits[0]
    dy = y_bin_limits[1] - y_bin_limits[0]

    x_bin_centres = x_bin_limits[:-1] + 0.5 * dx
    y_bin_centres = y_bin_limits[:-1] + 0.5 * dy

    bins_content_flat = bins_content.flatten()
    sort = np.argsort(bins_content_flat)
    sort = sort[::-1]

    bin_keys_list = []
    for i in range(len(x_bin_centres)):
        for j in range(len(y_bin_centres)):
            bin_keys_list.append((i,j))

    bins_info = OrderedDict()
    cred_region_index = 0
    integrated_post_prob = 0.0
    for si in sort:
        bin_key = bin_keys_list[si]
        i,j = bin_key
        xi = x_bin_centres[i]
        yj = y_bin_centres[j]

        # In posterior mode we take the z value to simply be 
        # the index of the corresponding credible region
        z_val = cred_region_index
        integrated_post_prob += 100. * bins_content[bin_key] * dx * dy
        # Avoid rounding errors
        if integrated_post_prob > 100.0:
            integrated_post_prob = 100.0
        if integrated_post_prob > credible_regions[cred_region_index]:
            cred_region_index += 1

        bin_count = bins_content_unweighted[bin_key]
        if bin_count > 0:
            bins_info[bin_key] = (xi, yj, z_val)

    z_min = 0
    z_max = len(credible_regions)

    # Set color limits
    color_z_lims = list(np.linspace(z_min, z_max, len(ccs.ccodes)+1))


    #
    # Generate string to be printed
    #

    # Define a function that returns the color code and marker for any bin 
    # coordinate xiyi in the plot
    def get_ccode_and_marker(xiyi):
        """Determines the color code and marker for a 2D posterior bin.

        The `z_val` from `bins_info` is the index of the credible region
        the bin belongs to. This index is used directly to select a color
        from `ccs.ccodes`. The marker is always `ms.regular_marker`.

        This function relies on `bins_info`, `z_min`, `z_max` (which define
        the range of credible region indices), `ccs` (CCodeSettings), and
        `ms` (MarkerSettings) from the outer scope.

        Args:
            xiyi (tuple): The (x_bin_index, y_bin_index) coordinates
                of the bin.

        Returns:
            tuple: `(ccode, marker)` where `ccode` is the color code (int)
                and `marker` is `ms.regular_marker`.
        """

        z_val = bins_info[xiyi][2]
        z_norm = 0.0
        if (z_max != z_min):
            z_norm = (z_val - z_min) / (z_max - z_min)
        if z_norm > 1.0:
            z_norm = 1.0
        elif z_norm < 0.0:
            z_norm = 0.0

        # Set color code
        ccode = None
        if z_norm == 1.0:
            ccode = ccs.ccodes[-1]
        elif z_norm == 0.0:
            ccode = ccs.ccodes[0]
        else:
            i = z_val
            ccode = ccs.ccodes[i]

        # Set marker
        marker = ms.regular_marker

        return ccode, marker


    # Pass the above function to utils.fill_plot, receive back the generated
    # plot (including axes) as a list of strings.
    plot_lines, fig_width = utils.fill_plot(xy_bins, bins_info, x_bin_limits,
                                            y_bin_limits, ccs, ms, 
                                            get_ccode_and_marker, ff,
                                            add_y_grid_lines=False)


    #
    # Add colorbar, legend, etc
    #
        
    # CR legend
    CR_legend_entries = []

    for i,cred_reg in enumerate(credible_regions[:-1]):
        cred_reg_str = "{:.12g}% CR".format(cred_reg)
        CR_legend_entries.append((ms.regular_marker.strip(), ccs.ccodes[i], 
                               cred_reg_str, ccs.fg_ccode))
    
    CR_legend, CR_legend_width = utils.generate_legend(CR_legend_entries, 
                                                 ccs.bg_ccode, sep="  ")


    # Legend: posterior max bin
    post_maxbin_legend_entries = []
    post_maxbin_index = np.unravel_index(np.argmax(bins_content), bins_content.shape)
    post_maxbin_content = bins_content[post_maxbin_index]
    post_maxbin_limits_x = [x_bin_limits[post_maxbin_index[0]], x_bin_limits[post_maxbin_index[0]+1]]
    post_maxbin_limits_y = [y_bin_limits[post_maxbin_index[1]], y_bin_limits[post_maxbin_index[1]+1]]
    
    post_maxbin_str = "posterior max bin:  x: "
    post_maxbin_str += ("(" + ff2 + ", " + ff2 + ")").format(post_maxbin_limits_x[0],
                                                             post_maxbin_limits_x[1])
    post_maxbin_str += "  y: "
    post_maxbin_str += ("(" + ff2 + ", " + ff2 + ")").format(post_maxbin_limits_y[0],
                                                             post_maxbin_limits_y[1])
    post_maxbin_str += "  bin height: "
    post_maxbin_str += (ff2).format(post_maxbin_content)

    post_maxbin_legend_entries.append(("", ccs.fg_ccode, post_maxbin_str, ccs.fg_ccode))

    post_maxbin_legend, post_maxbin_legend_width = utils.generate_legend(
        post_maxbin_legend_entries, ccs.bg_ccode, sep="  ", internal_sep=" ")


    # Legend: posterior mean point
    post_mean_legend_entries = []
    post_mean_str = "posterior mean point:  (x,y) = "
    post_mean_str += ("(" + ff2 + ", " + ff2 + ")").format(posterior_mean_x,
                                                           posterior_mean_y)

    post_mean_legend_entries.append(("", ccs.fg_ccode, post_mean_str, ccs.fg_ccode))

    post_mean_legend, post_mean_legend_width = utils.generate_legend(
        post_mean_legend_entries, ccs.bg_ccode, sep="  ", internal_sep=" ")


    # Empty line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode)
    # Insert CR legend
    plot_lines, fig_width = utils.insert_line(CR_legend, CR_legend_width, plot_lines,
                                              fig_width, ccs.fg_ccode, ccs.bg_ccode)
    # Empty line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode)
    # Insert maxbin legend
    plot_lines, fig_width = utils.insert_line(post_maxbin_legend, post_maxbin_legend_width, plot_lines,
                                              fig_width, ccs.fg_ccode, ccs.bg_ccode)
    # Empty line
    plot_lines, fig_width = utils.insert_line("", 0, plot_lines, fig_width,
                                              ccs.fg_ccode, ccs.bg_ccode)
    # Insert posterior mean legend
    plot_lines, fig_width = utils.insert_line(post_mean_legend, post_mean_legend_width, plot_lines, 
                                              fig_width, ccs.fg_ccode, ccs.bg_ccode)



    #
    # Add left padding
    #

    plot_lines = utils.add_left_padding(plot_lines, ccs.fg_ccode, ccs.bg_ccode)


    #
    # Set labels
    #

    x_label = x_name
    y_label = y_name
    w_label = w_name

    #
    # Add info text
    #

    plot_lines, fig_width = utils.add_info_text(
        plot_lines, fig_width, ccs.fg_ccode, ccs.bg_ccode, ff=ff2, 
        x_label=x_label, x_range=x_range, x_bin_width=dx,
        y_label=y_label, y_range=y_range, y_bin_width=dy,
        x_transf_expr=x_transf_expr, y_transf_expr=y_transf_expr,
        w_label=w_label, w_transf_expr=w_transf_expr,
        filter_names=filter_names, mode_name="posterior")


    #
    # Print everything
    #

    for line in plot_lines:
        print(line)

    return
