#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sup -- the Simlpe Unicode Plotter. 

A program for generating quick data visualisations directly in the terminal.

Example:
    Run the command 
  
        $ python3 sup.py --help
  
    to see a list of examples.

"""

import sys
import os
import time
import argparse
from sup import (
    colors, listmode, colorsmode, colormapsmode, plr2dmode, plr1dmode,
    maxmin2dmode, maxmin1dmode, avg1dmode, avg2dmode, hist1dmode, hist2dmode,
    post1dmode, post2dmode, graph1dmode, graph2dmode, chisq1dmode, chisq2dmode
    )
from sup.utils import SupRuntimeError, error_prefix
import sup.defaults as defaults

# Functions to add mode-specific arguments to subparsers
def _add_list_args(parser):
    """Adds arguments specific to the 'list' mode."""
    parser.add_argument("input_file", type=str, action="store", 
                                 help="path to the input data file")

def _add_hist1d_args(parser):
    """Adds arguments specific to the 'hist1d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser.add_argument("-n", "--normalize", action="store_true", dest="normalize_histogram", default=False, help="normalize histogram to integrate to unity")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_hist2d_args(parser):
    """Adds arguments specific to the 'hist2d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser.add_argument("-n", "--normalize", action="store_true", dest="normalize_histogram", default=False, help="normalize histogram to integrate to unity")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_maxmin1d_args(parser):
    """Adds arguments common to 'max1d' and 'min1d' modes."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_maxmin2d_args(parser):
    """Adds arguments common to 'max2d' and 'min2d' modes."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the max/min point(s)")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_avg1d_args(parser):
    """Adds arguments specific to the 'avg1d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_avg2d_args(parser):
    """Adds arguments specific to the 'avg2d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_post1d_args(parser):
    """Adds arguments specific to the 'post1d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser.add_argument("-cr", "--credible-regions", nargs="+", type=float, action="store", dest="credible_regions", default=None, help="list of probabilities (in percent) to define the credible regions", metavar="CR_PROB")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_post2d_args(parser):
    """Adds arguments specific to the 'post2d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser.add_argument("-cr", "--credible-regions", nargs="+", type=float, action="store", dest="credible_regions", default=None, help="list of probabilities (in percent) to define the credible regions", metavar="CR_PROB")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_plr1d_args(parser):
    """Adds arguments specific to the 'plr1d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-cl", "--confidence-levels", nargs="+", type=float, action="store", dest="confidence_levels", default=None, help="list of probabilities (in percent) to define the confidence levels", metavar="CL_PROB")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value", metavar="CAP_VAL")
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_chisq1d_args(parser):
    """Adds arguments specific to the 'chisq1d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset (used to calculate chi-square)")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range (for delta chi-square)", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value before chi-square calculation", metavar="CAP_VAL")
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_plr2d_args(parser):
    """Adds arguments specific to the 'plr2d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-cl", "--confidence-levels", nargs="+", type=float, action="store", dest="confidence_levels", default=None, help="list of probabilities (in percent) to define the confidence levels", metavar="CL_PROB")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value", metavar="CAP_VAL")
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=4, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the max likelihood point(s)")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_chisq2d_args(parser):
    """Adds arguments specific to the 'chisq2d' mode."""
    parser.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset (used to calculate chi-square)")
    parser.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices of boolean datasets used for filtering", metavar="F_INDEX")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    # For chisq2d, z_range applies to delta chi-square values
    parser.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range (for delta chi-square)", metavar=("Z_MIN", "Z_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value before chi-square calculation", metavar="CAP_VAL")
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    # Added n_colors argument for chisq2d, similar to hist2d
    parser.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=None, help="number of colors in colorbar (max 10, default 5 for chisq2d)", metavar="N_COLORS")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=4, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the min chi-square point(s)")
    parser.add_argument("-rs", "--read-slice", nargs=3, type=int, action="store", dest="read_slice", default=[0,-1,1], help="read only the given slice of each dataset", metavar=("START", "END", "STEP"))
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")
    parser.add_argument("-dl", "--delimiter", type=str, action="store", dest="delimiter", default=" ", help="set the delimiter used in the input data file (only for text files)", metavar="DELIMITER")
    parser.add_argument("-wa", "--watch", type=float, action="store", dest="watch_n_seconds", default=None, help="regenerate the plot at fixed time intervals", metavar="N_SECONDS")

def _add_graph1d_args(parser):
    """Adds arguments specific to the 'graph1d' mode."""
    parser.add_argument("function", type=str, action="store", help="definition of function f(x), using numpy as 'np' (e.g. \"x * np.sin(x)\")")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")

def _add_graph2d_args(parser):
    """Adds arguments specific to the 'graph2d' mode."""
    parser.add_argument("function", type=str, action="store", help="definition of function f(x,y), using numpy as 'np' (e.g. \"y * np.sin(x)\")")
    parser.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="z-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser.add_argument("-sz", "--size", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="plot size in terms of number of grid cells (bins) for each axis", metavar=("X_SIZE", "Y_SIZE"))
    parser.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish, 2 = inferno-ish, 3 = blue-red-ish, 4 = gambit-ish", metavar="CM")
    parser.add_argument("-rc", "--reverse-colormap", action="store_true", dest="reverse_colormap", default=False, help="reverse colormap")
    parser.add_argument("-d", "--decimals", type=int, action="store", dest="n_decimals", default=defaults.n_decimals, help="set the number of decimals for axis and colorbar tick labels", metavar="N_DECIMALS")

# No arguments needed for colors and colormaps modes beyond what subparser.add_parser provides.

def main():
    """The sup main function.

    This function parses the command line arguments using argparse and runs 
    the sup in the requested mode.
    
    Returns:
        (int): An error code that equals 0 (success) or 1 (error occurred).

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
  sup chisq1d     plot the delta chi-square across the x axis
  sup chisq2d     plot the delta chi-square across the (x,y) plane
  sup graph1d     plot the function y = f(x) across the x axis
  sup graph2d     plot the function z = f(x,y) across the (x,y) plane
  sup colormaps   display the available colormaps
  sup colors      display the colors available for creating colormaps (for development)

examples:
  sup list data.hdf5

  sup list data.txt --delimiter ","

  sup hist1d data.txt 0 --x-range -10 10 --size 100 20 --y-transf "np.log10(y)" --delimiter ","

  sup hist2d data.txt 0 1 --x-range -10 10 --y-range -10 10 --size 30 30 --delimiter "," --colormap 1

  sup post2d posterior.dat 2 3 --x-range -10 10 --y-range -10 10 --size 30 30 --delimiter " "

  sup plr2d data.hdf5 0 1 4 --x-range 0 10 --y-range 0 10 --size 20 20

  sup plr2d data.hdf5 2 1 4 --x-range 0 10 --y-range 0 20 --size 20 40 --x-transf "np.abs(x)"

  sup graph1d "x * np.cos(2 * np.pi * x)" --x-range 0.0 2.0 --y-range -2 2 --size 40 20 --white-bg

  sup graph2d "np.sin(x**2 + y**2) / (x**2 + y**2)" --x-range -5 5 --y-range -5 5 --size 50 50

"""
    )
    subparsers = parser.add_subparsers(dest="mode")

    # Parser for "list" mode
    parser_listmode = subparsers.add_parser("list")
    parser_listmode.set_defaults(func=listmode.run)
    _add_list_args(parser_listmode)

    # Parser for "hist1d" mode
    parser_hist1dmode = subparsers.add_parser("hist1d")
    parser_hist1dmode.set_defaults(func=hist1dmode.run)
    _add_hist1d_args(parser_hist1dmode)

    # Parser for "hist2d" mode
    parser_hist2dmode = subparsers.add_parser("hist2d")
    parser_hist2dmode.set_defaults(func=hist2dmode.run)
    _add_hist2d_args(parser_hist2dmode)

    # Parser for "max1d" mode
    parser_max1dmode = subparsers.add_parser("max1d")
    parser_max1dmode.set_defaults(func=maxmin1dmode.run_max)
    _add_maxmin1d_args(parser_max1dmode)

    # Parser for "min1d" mode
    parser_min1dmode = subparsers.add_parser("min1d")
    parser_min1dmode.set_defaults(func=maxmin1dmode.run_min)
    _add_maxmin1d_args(parser_min1dmode) # Uses the same args as max1d

    # Parser for "max2d" mode
    parser_max2dmode = subparsers.add_parser("max2d")
    parser_max2dmode.set_defaults(func=maxmin2dmode.run_max)
    _add_maxmin2d_args(parser_max2dmode)

    # Parser for "min2d" mode
    parser_min2dmode = subparsers.add_parser("min2d")
    parser_min2dmode.set_defaults(func=maxmin2dmode.run_min)
    _add_maxmin2d_args(parser_min2dmode) # Uses the same args as max2d

    # Parser for "avg1d" mode
    parser_avg1dmode = subparsers.add_parser("avg1d")
    parser_avg1dmode.set_defaults(func=avg1dmode.run)
    _add_avg1d_args(parser_avg1dmode)

    # Parser for "avg2d" mode
    parser_avg2dmode = subparsers.add_parser("avg2d")
    parser_avg2dmode.set_defaults(func=avg2dmode.run)
    _add_avg2d_args(parser_avg2dmode)

    # Parser for "post1d" mode
    parser_post1dmode = subparsers.add_parser("post1d")
    parser_post1dmode.set_defaults(func=post1dmode.run)
    _add_post1d_args(parser_post1dmode)

    # Parser for "post2d" mode
    parser_post2dmode = subparsers.add_parser("post2d")
    parser_post2dmode.set_defaults(func=post2dmode.run)
    _add_post2d_args(parser_post2dmode)

    # Parser for "plr1d" mode
    parser_plr1dmode = subparsers.add_parser("plr1d")
    parser_plr1dmode.set_defaults(func=plr1dmode.run)
    _add_plr1d_args(parser_plr1dmode)

    # Parser for "plr2d" mode
    parser_plr2dmode = subparsers.add_parser("plr2d")
    parser_plr2dmode.set_defaults(func=plr2dmode.run)
    _add_plr2d_args(parser_plr2dmode)

    # Parser for "chisq1d" mode
    parser_chisq1dmode = subparsers.add_parser("chisq1d")
    parser_chisq1dmode.set_defaults(func=chisq1dmode.run)
    _add_chisq1d_args(parser_chisq1dmode)

    # Parser for "chisq2d" mode
    parser_chisq2dmode = subparsers.add_parser("chisq2d")
    parser_chisq2dmode.set_defaults(func=chisq2dmode.run)
    _add_chisq2d_args(parser_chisq2dmode)

    # Parser for "graph1d" mode
    parser_graph1dmode = subparsers.add_parser("graph1d")
    parser_graph1dmode.set_defaults(func=graph1dmode.run)
    _add_graph1d_args(parser_graph1dmode)

    # Parser for "graph2d" mode
    parser_graph2dmode = subparsers.add_parser("graph2d")
    parser_graph2dmode.set_defaults(func=graph2dmode.run)
    _add_graph2d_args(parser_graph2dmode)

    # Parser for "colors" mode
    parser_colorsmode = subparsers.add_parser("colors")
    parser_colorsmode.set_defaults(func=colorsmode.run)
    # No specific arguments for colors mode using an _add_args function

    # Parser for "colormaps" mode
    parser_colormapsmode = subparsers.add_parser("colormaps")
    parser_colormapsmode.set_defaults(func=colormapsmode.run)
    # No specific arguments for colormaps mode using an _add_args function

    # Parse arguments and perform some consistency checks
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_usage()
        return 1

    args_dict = vars(args)

    # Must check watch_n_seconds before other checks that might depend on do_watch,
    # and before do_watch itself is set.
    if "watch_n_seconds" in args_dict and args.watch_n_seconds is not None:
        if args.watch_n_seconds <= 0.0:
            try:
                raise SupRuntimeError("N_SECONDS must be greater than 0")
            except SupRuntimeError as e:
                print("{} {}".format(error_prefix, e))
                return 1 
        do_watch = True
    else:
        do_watch = False

    # Consistency checks:
    try:
        # The input_file check should only occur if not in watch mode.
        # In watch mode, the file might not exist initially, and the loop handles this.
        if "input_file" in args_dict and not do_watch:
            if not os.path.isfile(args.input_file):
                raise SupRuntimeError("File not found:"
                                      " {}".format(args.input_file))

        if "x_range" in args_dict:
            if args.x_range is not None:
                if args.x_range[0] >= args.x_range[1]:
                    raise SupRuntimeError("X_MIN must be smaller than X_MAX")

        if "y_range" in args_dict:
            if args.y_range is not None:
                if args.y_range[0] >= args.y_range[1]:
                    raise SupRuntimeError("Y_MIN must be smaller than Y_MAX")

        if "z_range" in args_dict:
            if args.z_range is not None:
                if args.z_range[0] >= args.z_range[1]:
                    raise SupRuntimeError("Z_MIN must be smaller than Z_MAX")

        if "xy_bins" in args_dict:
            if args.xy_bins is not None:
                if (args.xy_bins[0] < 6) or (args.xy_bins[1] < 6):
                    raise SupRuntimeError("X_BINS and Y_BINS must be greater "
                                          "than 6")

        if "n_colors" in args_dict:
            if args.n_colors is not None:
                if (args.n_colors < 1) or (args.n_colors > 10):
                    raise SupRuntimeError("N_COLORS must be an integer between "
                                          "1 and 10")

        if "cmap_index" in args_dict:
            if args.cmap_index is not None:
                n_colormaps = len(colors.cmaps)
                if args.cmap_index not in range(n_colormaps):
                    raise SupRuntimeError("the colormap option (CM) must be an "
                                          "integer between 0 and "
                                          + format(n_colormaps - 1))

        if "read_slice" in args_dict:
            if args.read_slice is not None:
                if args.read_slice[2] <= 0:  # read_slice is [START, END, STEP]
                    raise SupRuntimeError("STEP must be an integer greater "
                                          "than 0")

        if "n_decimals" in args_dict:
            if args.n_decimals is not None:
                if (args.n_decimals < 1) or (args.n_decimals > 8):
                    raise SupRuntimeError("N_DECIMALS must be an integer "
                                          "between 1 and 8")

        if "credible_regions" in args_dict:
            if args.credible_regions is not None:
                for cr_val in args.credible_regions:
                    if not (0. <= cr_val <= 100.):
                        raise SupRuntimeError("CR_PROB (credible region "
                                              "probability) must be between 0 "
                                              "and 100")

        if "confidence_levels" in args_dict:
            if args.confidence_levels is not None:
                for cl_val in args.confidence_levels:
                    if not (0. <= cl_val <= 100.):
                        raise SupRuntimeError("CL_PROB (confidence level "
                                              "probability) must be between 0 "
                                              "and 100")
        
    except SupRuntimeError as e:
        print("{} {}".format(error_prefix, e))
        return 1


    # Now try running sup in the chosen mode.
    try:
        # If the watch flag is in use, run the chosen sup mode repeatedly until 
        # the user hits ctrl+c.
        if do_watch:

            keep_going = True

            while keep_going:

                message = ""

                # If input file is *not* found:
                if not os.path.isfile(args.input_file):
                    message += ("File not found: {}\n".format(args.input_file))
                    message += ("Trying again in {} seconds. Press CTRL+C to "
                                "abort.".format(args.watch_n_seconds))
                # If input file *is* found:
                else:
                    args.func(args)

                    message += ("Regenerating the plot in {} seconds. Press "
                                "CTRL+C to abort.".format(args.watch_n_seconds))

                # Print message
                print()
                print("\033[1m" + message + "\033[0m")  # Use bold text
                print()

                # Sleep, then repeat (unless the user aborts)
                try:
                    time.sleep(args.watch_n_seconds)
                except KeyboardInterrupt:
                    keep_going = False

        # Else, run once
        else:
            args.func(args)

    except SupRuntimeError as e:
        print("{} {}".format(error_prefix, e))
        return 1

    except BaseException as e:
        print("{} Unexpected error:".format(error_prefix))
        print()
        raise e

    return 0


if __name__ == "__main__":
    sys.exit(main())
    
