# -*- coding: utf-8 -*-

"""sup -- the Simlpe Unicode Plotter. 

A program for generating quick data visualisation directly in the terminal.

Example:
    Run the command 
  
        $ python3 sup.py --help
  
    to see a list of examples.

Todo:
    * Add a "--watch N" option which generates the same plot every N-th second.

"""

import sys
import os
import argparse
from sup import colors, listmode, colorsmode, colormapsmode, plr2dmode, plr1dmode, maxmin2dmode, maxmin1dmode, avg1dmode, avg2dmode, hist1dmode, hist2dmode, post1dmode, post2dmode, graph1dmode, graph2dmode


def main():
    """The main function.

    This function parses the command line arguments using argparse and runs 
    the sup in the requested mode.

    Raises:
        RuntimeError: If the chosen sup mode fails raises an Exception.

    """

    # Get the script name
    prog_name = os.path.basename(sys.argv[0])

    # Top-level parser
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="sup -- the Simple Unicode Plotter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
modes:
  sup list        list dataset names and indices
  sup hist1d      plot the x histogram
  sup hist2d      plot the (x,y) histogram
  sup max1d       plot the maximum y value across the x axis
  sup max2d       plot the maximum z value across the (x,y) plane
  sup min1d       plot the minimum y value across the x axis
  sup min2d       plot the minimum z value across the (x,y) plane
  sup avg1d       plot the average y value across the x axis
  sup avg2d       plot the average z value across the (x,y) plane
  sup post1d      plot the x posterior probability distribution
  sup post2d      plot the (x,y) posterior probability distribution
  sup plr1d       plot the profile likelihood ratio across the x axis
  sup plr2d       plot the profile likelihood ratio across the (x,y) plane
  sup graph1d     plot the function y = f(x) across the x axis
  sup graph2d     plot the function z = f(x,y) across the (x,y) plane
  sup colormaps   display the available colormaps
  sup colors      display the colors available for creating colormaps (for development)

examples:
  ./sup.py list data.hdf5

  ./sup.py list data.txt --delimiter ","

  ./sup.py hist1d data.txt 0 --x-range -10 10 --size 100 20 --y-transf "np.log10(y)" --delimiter ","

  ./sup.py hist2d data.txt 0 1 --x-range -10 10 --y-range -10 10 --size 30 30 --delimiter "," --colormap 1

  ./sup.py post2d posterior.dat 2 3 --x-range -10 10 --y-range -10 10 --size 30 30 --delimiter " "

  ./sup.py plr2d data.hdf5 0 1 4 --x-range 0 10 --y-range 0 10 --size 20 20

  ./sup.py plr2d data.hdf5 2 1 4 --x-range 0 10 --y-range 0 20 --size 20 40 --x-transf "np.abs(x)"

  ./sup.py graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 --size 40 20 --white-bg

  ./sup.py graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 --size 50 50

"""
    )
    subparsers = parser.add_subparsers(dest="mode")

    # Parser for "list" mode
    parser_listmode = subparsers.add_parser("list")
    parser_listmode.set_defaults(func=listmode.run)
    parser_listmode.add_argument("input_file", type=str, action="store", help="path to the input data file")

    # Parser for "hist1d" mode
    parser_hist1dmode = subparsers.add_parser("hist1d")
    parser_hist1dmode.set_defaults(func=hist1dmode.run)
    parser_hist1dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_hist1dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_hist1dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_hist1dmode.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser_hist1dmode.add_argument("-n", "--normalize", action="store_true", dest="normalize_histogram", default=False, help="normalize histogram to integrate to unity")
    parser_hist1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_hist1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_hist1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_hist1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_hist1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_hist1dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_hist1dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_hist1dmode.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser_hist1dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_hist1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_hist1dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "hist2d" mode
    parser_hist2dmode = subparsers.add_parser("hist2d")
    parser_hist2dmode.set_defaults(func=hist2dmode.run)
    parser_hist2dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_hist2dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_hist2dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_hist2dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_hist2dmode.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser_hist2dmode.add_argument("-n", "--normalize", action="store_true", dest="normalize_histogram", default=False, help="normalize histogram to integrate to unity")
    parser_hist2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_hist2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_hist2dmode.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser_hist2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_hist2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_hist2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_hist2dmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_hist2dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_hist2dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_hist2dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_hist2dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_hist2dmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_hist2dmode.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser_hist2dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_hist2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_hist2dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "max1d" mode
    parser_max1dmode = subparsers.add_parser("max1d")
    parser_max1dmode.set_defaults(func=maxmin1dmode.run_max)
    parser_max1dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_max1dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_max1dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_max1dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_max1dmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_max1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_max1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_max1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_max1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_max1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_max1dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_max1dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_max1dmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser_max1dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_max1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_max1dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "min1d" mode
    parser_min1dmode = subparsers.add_parser("min1d")
    parser_min1dmode.set_defaults(func=maxmin1dmode.run_min)
    parser_min1dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_min1dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_min1dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_min1dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_min1dmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_min1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_min1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_min1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_min1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_min1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_min1dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_min1dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_min1dmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser_min1dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_min1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_min1dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "max2d" mode
    parser_max2dmode = subparsers.add_parser("max2d")
    parser_max2dmode.set_defaults(func=maxmin2dmode.run_max)
    parser_max2dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_max2dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_max2dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_max2dmode.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    parser_max2dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_max2dmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_max2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_max2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_max2dmode.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser_max2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_max2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_max2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_max2dmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_max2dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_max2dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_max2dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_max2dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_max2dmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_max2dmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser_max2dmode.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the max/min point(s)")
    parser_max2dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_max2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_max2dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "min2d" mode
    parser_min2dmode = subparsers.add_parser("min2d")
    parser_min2dmode.set_defaults(func=maxmin2dmode.run_min)
    parser_min2dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_min2dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_min2dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_min2dmode.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    parser_min2dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_min2dmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_min2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_min2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_min2dmode.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser_min2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_min2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_min2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_min2dmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_min2dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_min2dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_min2dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_min2dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_min2dmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_min2dmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser_min2dmode.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker the for the max/min point(s)")
    parser_min2dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_min2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_min2dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "avg1d" mode
    parser_avg1dmode = subparsers.add_parser("avg1d")
    parser_avg1dmode.set_defaults(func=avg1dmode.run)
    parser_avg1dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_avg1dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_avg1dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_avg1dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_avg1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_avg1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_avg1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_avg1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_avg1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_avg1dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_avg1dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_avg1dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_avg1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_avg1dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "avg2d" mode
    parser_avg2dmode = subparsers.add_parser("avg2d")
    parser_avg2dmode.set_defaults(func=avg2dmode.run)
    parser_avg2dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_avg2dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_avg2dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_avg2dmode.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    parser_avg2dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_avg2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_avg2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_avg2dmode.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser_avg2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_avg2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_avg2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_avg2dmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_avg2dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_avg2dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_avg2dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_avg2dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_avg2dmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_avg2dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_avg2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_avg2dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "post1d" mode
    parser_post1dmode = subparsers.add_parser("post1d")
    parser_post1dmode.set_defaults(func=post1dmode.run)
    parser_post1dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_post1dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_post1dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_post1dmode.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser_post1dmode.add_argument("-cr", "--credible-regions", nargs="+", type=float, action="store", dest="credible_regions", default=None, help="list of probabilities (in percent) to define the credible regions", metavar="CR_PROB")
    parser_post1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_post1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_post1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_post1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_post1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_post1dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_post1dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_post1dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_post1dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_post1dmode.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser_post1dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_post1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_post1dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "post2d" mode
    parser_post2dmode = subparsers.add_parser("post2d")
    parser_post2dmode.set_defaults(func=post2dmode.run)
    parser_post2dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_post2dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_post2dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_post2dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_post2dmode.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser_post2dmode.add_argument("-cr", "--credible-regions", nargs="+", type=float, action="store", dest="credible_regions", default=None, help="list of probabilities (in percent) to define the credible regions", metavar="CR_PROB")
    parser_post2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_post2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_post2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_post2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_post2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_post2dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_post2dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_post2dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_post2dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_post2dmode.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser_post2dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_post2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_post2dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "plr1d" mode
    parser_plr1dmode = subparsers.add_parser("plr1d")
    parser_plr1dmode.set_defaults(func=plr1dmode.run)
    parser_plr1dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_plr1dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_plr1dmode.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset")
    parser_plr1dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_plr1dmode.add_argument("-cl", "--confidence-levels", nargs="+", type=float, action="store", dest="confidence_levels", default=None, help="list of probabilities (in percent) to define the confidence levels", metavar="CL_PROB")
    parser_plr1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_plr1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_plr1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_plr1dmode.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value", metavar="CAP_VAL")
    parser_plr1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_plr1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_plr1dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_plr1dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_plr1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_plr1dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "plr2d" mode
    parser_plr2dmode = subparsers.add_parser("plr2d")
    parser_plr2dmode.set_defaults(func=plr2dmode.run)
    parser_plr2dmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_plr2dmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_plr2dmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_plr2dmode.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset")
    parser_plr2dmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser_plr2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_plr2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_plr2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_plr2dmode.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value", metavar="CAP_VAL")
    parser_plr2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_plr2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_plr2dmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_plr2dmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_plr2dmode.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the max likelihood point(s)")
    parser_plr2dmode.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser_plr2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser_plr2dmode.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")

    # Parser for "graph1d" mode
    parser_graph1dmode = subparsers.add_parser("graph1d")
    parser_graph1dmode.set_defaults(func=graph1dmode.run)
    parser_graph1dmode.add_argument("function", type=str, action="store", help="definition of function f(x), using numpy as 'np' (e.g. \"x * np.sin(x)\")")
    parser_graph1dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_graph1dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_graph1dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_graph1dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_graph1dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_graph1dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")

    # Parser for "graph2d" mode
    parser_graph2dmode = subparsers.add_parser("graph2d")
    parser_graph2dmode.set_defaults(func=graph2dmode.run)
    parser_graph2dmode.add_argument("function", type=str, action="store", help="definition of function f(x,y), using numpy as 'np' (e.g. \"y * np.sin(x)\")")
    parser_graph2dmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_graph2dmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_graph2dmode.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser_graph2dmode.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser_graph2dmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_graph2dmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_graph2dmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_graph2dmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish", metavar="CM")
    parser_graph2dmode.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser_graph2dmode.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=2, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")

    # Parser for "colors" mode
    parser_colorsmode = subparsers.add_parser("colors")
    parser_colorsmode.set_defaults(func=colorsmode.run)

    # Parser for "colormaps" mode
    parser_colormapsmode = subparsers.add_parser("colormaps")
    parser_colormapsmode.set_defaults(func=colormapsmode.run)

    # Parse arguments and perform some consistency checks
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    error_prefix = os.path.basename(__file__) + ": error: "
    args_dict = vars(args)

    if "x_range" in args_dict.keys():
        if args.x_range is not None:
            if args.x_range[0] >= args.x_range[1]:
                print(error_prefix + "X_MIN must be smaller than X_MAX")
                return

    if "y_range" in args_dict.keys():
        if args.y_range is not None:
            if args.y_range[0] >= args.y_range[1]:
                print(error_prefix + "Y_MIN must be smaller than Y_MAX")
                return

    if "z_range" in args_dict.keys():
        if args.z_range is not None:
            if args.z_range[0] >= args.z_range[1]:
                print(error_prefix + "Z_MIN must be smaller than Z_MAX")
                return

    if "xy_bins" in args_dict.keys():
        if args.xy_bins is not None:
            if (args.xy_bins[0] < 6) or (args.xy_bins[1] < 6):
                print(error_prefix + "X_BINS and Y_BINS must be at least 6")
                return

    if "n_colors" in args_dict.keys():
        if args.n_colors is not None:
            if (args.n_colors < 1) or (args.n_colors > 10):
                print(error_prefix + "N_COLORS must be an integer between 1 and 10")
                return

    if "cmap_index" in args_dict.keys():
        if args.cmap_index is not None:
            n_colormaps = len(colors.cmaps)
            if args.cmap_index not in range(n_colormaps):
                print(error_prefix + "the colormap option (CM) must be a integer between 0 and " + str(n_colormaps))
                return

    if "read_slice" in args_dict.keys():
        if args.read_slice is not None:
            if args.read_slice[2] <= 0:
                print(error_prefix + "STEP must be an integer greater than 0")
                return

    if "n_decimals" in args_dict.keys():
        if args.n_decimals is not None:
            if (args.n_decimals < 1) or (args.n_decimals > 8):
                print(error_prefix + "N_DECIMALS must be an integer between 1 and 8")
                return

    if "credible_regions" in args_dict.keys():
        if args.credible_regions is not None:
            for cr_val in args.credible_regions:
                if (cr_val < 0.) or (cr_val > 100.):
                    print(error_prefix + "CR_PROB (credible region probability) must be between 0 and 100")
                    return 

    if "confidence_levels" in args_dict.keys():
        if args.confidence_levels is not None:
            for cl_val in args.confidence_levels:
                if (cl_val < 0.) or (cl_val > 100.):
                    print(error_prefix + "CL_PROB (confidence level probability) must be between 0 and 100")
                    return 

    # Try running sup in the chosen mode
    try:
        args.func(args)
    except RuntimeError as e:
        print(error_prefix + "{0}".format(e))
    except BaseException as e:
        print(error_prefix + "Unexpected error:")
        print()
        raise e

if __name__ == "__main__":
    main()
