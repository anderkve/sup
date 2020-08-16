#! /usr/bin/env python3

"""
sup -- the Simlpe Unicode Plotter 

modes:
  sup list    list dataset names and indices
  sup colors  display the colors available for colormaps
  sup plr     plot the profile likeliood ratio
  sup max     plot the maximum z value
  sup min     plot the minimum z value
  sup avg     plot the average z value
  sup hist    plot a histogram 
  # sup post    plot the z posterior probability density

examples:
  ./sup.py list data.hdf5

  ./sup.py plr data.hdf5 0 1 4 --x-range 0 10 --y-range 0 10 --bins 20 20

  ./sup.py plr data.hdf5 2 1 4 --x-range 0 10 --y-range 0 10 --bins 20 20 -g

  ./sup.py plr data.hdf5 2 1 4 --x-range 0 10 --y-range 0 20 --bins 20 40 --x-transf "np.abs(x)"
"""

import sys
import os
import argparse
from sup import listmode, colorsmode, plrmode, maxminmode, avgmode, histmode


def main():
    
    #
    # Parse and check command line arguments
    #

    # Get the script name
    prog_name = os.path.basename(sys.argv[0])

    # Top-level parser
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="sup -- the Simple Unicode Plotter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
modes:
  sup list    list dataset names and indices
  sup colors  display the colors available for colormaps
  sup plr     plot the profile likeliood ratio
  sup max     plot the maximum z value
  sup min     plot the minimum z value
  sup avg     plot the average z value
  sup hist    plot a histogram

examples:
  ./sup.py list data.hdf5

  ./sup.py plr data.hdf5 0 1 4 --x-range 0 10 --y-range 0 10 --bins 20 20

  ./sup.py plr data.hdf5 2 1 4 --x-range 0 10 --y-range 0 10 --bins 20 20 -g

  ./sup.py plr data.hdf5 2 1 4 --x-range 0 10 --y-range 0 20 --bins 20 40 --x-transf "np.abs(x)"
        """,
  # sup post    plot the z posterior probability density
    )
    subparsers = parser.add_subparsers(dest="mode")


    # Parser for "list" mode
    parser_listmode = subparsers.add_parser("list")
    parser_listmode.set_defaults(func=listmode.run)
    parser_listmode.add_argument("input_file", type=str, action="store", help="path to the input data file")

    # Parser for "colors" mode
    parser_colorsmode = subparsers.add_parser("colors")
    parser_colorsmode.set_defaults(func=colorsmode.run)

    # Parser for "plr" mode
    parser_plrmode = subparsers.add_parser("plr")
    parser_plrmode.set_defaults(func=plrmode.run)
    parser_plrmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_plrmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_plrmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_plrmode.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset")
    parser_plrmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices for boolean datasets used for filtering", metavar="F_INDEX")
    parser_plrmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_plrmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_plrmode.add_argument("-b", "--bins", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="number of bins for each axis", metavar=("X_BINS", "Y_BINS"))
    parser_plrmode.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value", metavar="CAP_VAL")
    parser_plrmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_plrmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_plrmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_plrmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")

    # Parser for "max" mode
    parser_maxmode = subparsers.add_parser("max")
    parser_maxmode.set_defaults(func=maxminmode.run_max)
    parser_maxmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_maxmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_maxmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_maxmode.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    # parser_maxmode.add_argument("-f", "--filter", nargs="+", type=int, action="store", dest="filter_indices", default=None, help="indices for boolean datasets used for filtering", metavar="F_INDEX")
    parser_maxmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_maxmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_maxmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_maxmode.add_argument("-b", "--bins", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="number of bins for each axis", metavar=("X_BINS", "Y_BINS"))
    parser_maxmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_maxmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_maxmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_maxmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish", metavar="CM")
    parser_maxmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_maxmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_maxmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_maxmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser_maxmode.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the max/min point(s)")

    # Parser for "min" mode
    parser_minmode = subparsers.add_parser("min")
    parser_minmode.set_defaults(func=maxminmode.run_min)
    parser_minmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_minmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_minmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_minmode.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    parser_minmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_minmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_minmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_minmode.add_argument("-b", "--bins", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="number of bins for each axis", metavar=("X_BINS", "Y_BINS"))
    parser_minmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_minmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_minmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_minmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish", metavar="CM")
    parser_minmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_minmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_minmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_minmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    parser_minmode.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker the for the max/min point(s)")

    # Parser for "avg" mode
    parser_avgmode = subparsers.add_parser("avg")
    parser_avgmode.set_defaults(func=avgmode.run)
    parser_avgmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_avgmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_avgmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_avgmode.add_argument("z_index", type=int, action="store", help="index of the z-axis dataset")
    # parser_avgmode.add_argument("-s", "--sort", type=int, action="store", dest="s_index", default=None, help="index of the sort dataset", metavar="S_INDEX")
    parser_avgmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_avgmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_avgmode.add_argument("-b", "--bins", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="number of bins for each axis", metavar=("X_BINS", "Y_BINS"))
    parser_avgmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_avgmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_avgmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_avgmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish", metavar="CM")
    parser_avgmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_avgmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_avgmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    # parser_avgmode.add_argument("-st", "--s-transf", type=str, action="store", dest="s_transf_expr", default="", help="tranformation for the sort dataset, using numpy as 'np' (e.g. -st \"np.log10(s)\")", metavar="EXPR")
    # parser_avgmode.add_argument("-ns", "--no-star", action="store_true", dest="no_star", default=False, help="switch off the star marker for the max/min point(s)")

    # Parser for "hist" mode
    parser_histmode = subparsers.add_parser("hist")
    parser_histmode.set_defaults(func=histmode.run)
    parser_histmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_histmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_histmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_histmode.add_argument("-w", "--weights", type=int, action="store", dest="w_index", default=None, help="index of the weights dataset", metavar="W_INDEX")
    parser_histmode.add_argument("-xr", "--x-range", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_histmode.add_argument("-yr", "--y-range", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_histmode.add_argument("-zr", "--z-range", nargs=2, type=float, action="store", dest="z_range", default=None, help="y-axis range", metavar=("Z_MIN", "Z_MAX"))
    parser_histmode.add_argument("-b", "--bins", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="number of bins for each axis", metavar=("X_BINS", "Y_BINS"))
    parser_histmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_histmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")
    parser_histmode.add_argument("-nc", "--num-colors", type=int, action="store", dest="n_colors", default=10, help="number of colors in colorbar (max 10)", metavar="N_COLORS")
    parser_histmode.add_argument("-cm", "--colormap", type=int, action="store", dest="cmap_index", default=0, help="select colormap: 0 = viridis-ish, 1 = jet-ish", metavar="CM")
    parser_histmode.add_argument("-xt", "--x-transf", type=str, action="store", dest="x_transf_expr", default="", help="tranformation for the x-axis dataset, using numpy as 'np' (e.g. -xt \"np.log10(x)\")", metavar="EXPR")
    parser_histmode.add_argument("-yt", "--y-transf", type=str, action="store", dest="y_transf_expr", default="", help="tranformation for the y-axis dataset, using numpy as 'np' (e.g. -yt \"np.log10(y)\")", metavar="EXPR")
    parser_histmode.add_argument("-zt", "--z-transf", type=str, action="store", dest="z_transf_expr", default="", help="tranformation for the z-axis dataset, using numpy as 'np' (e.g. -zt \"np.log10(z)\")", metavar="EXPR")
    parser_histmode.add_argument("-wt", "--w-transf", type=str, action="store", dest="w_transf_expr", default="", help="tranformation for the weights dataset, using numpy as 'np' (e.g. -zt \"np.ones(w.shape\")", metavar="EXPR")


    # Parse the arguments
    args = parser.parse_args()

    # If no arguments, print usage string and exit
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    # Run the function for the chosen mode
    args.func(args)


if __name__ == "__main__":
    main()
