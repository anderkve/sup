#! /usr/bin/env python3

"""
sup -- the Simlpe Unicode Plotter 

Modes:
  sup list      : list datasets 
  sup max       : plot the maximum z value per bin
  sup min       : plot the minimum z value per bin
  sup avg       : plot the average z value per bin
  sup plr       : plot the profile likeliood ratio per bin
  sup dens      : plot the density in each bin
  sup post      : plot the posterior density in each bin

Examples:

  ./sup.py plotinput.hdf5 121 143 160 
                --nxbins=40 --nybins=40 --xmin=0 --xmax=2000 --ymin=0 --ymax=2000

  ./sup.py input.hdf5 121 143 160 --llr
                --nxbins=40 --nybins=40 --xmin=0 --xmax=2000 --ymin=0 --ymax=2000

"""

import sys
import os
import argparse
import numpy as np
import h5py
from sup.utils import get_bin_tuples, get_dataset_names
from sup.colors import color_codes, n_colors
from sup import listmode, plrmode


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
        # epilog="""
        # Add a description here
        # """,
    )
    subparsers = parser.add_subparsers(dest='mode')


    # Parser for "list" mode
    parser_listmode = subparsers.add_parser('list')
    parser_listmode.set_defaults(func=listmode.run)
    parser_listmode.add_argument("input_file", type=str, action="store", help="path to the input data file")

    # Parser for "plr" mode
    parser_plrmode = subparsers.add_parser('plr')
    parser_plrmode.set_defaults(func=plrmode.run)
    parser_plrmode.add_argument("input_file", type=str, action="store", help="path to the input data file")
    parser_plrmode.add_argument("x_index", type=int, action="store", help="index of the x-axis dataset")
    parser_plrmode.add_argument("y_index", type=int, action="store", help="index of the y-axis dataset")
    parser_plrmode.add_argument("loglike_index", type=int, action="store", help="index of the ln(L) dataset")
    parser_plrmode.add_argument("-xr", "--xrange", nargs=2, type=float, action="store", dest="x_range", default=None, help="x-axis range", metavar=("X_MIN", "X_MAX"))
    parser_plrmode.add_argument("-yr", "--yrange", nargs=2, type=float, action="store", dest="y_range", default=None, help="y-axis range", metavar=("Y_MIN", "Y_MAX"))
    parser_plrmode.add_argument("-b", "--bins", nargs=2, type=int, action="store", dest="xy_bins", default=None, help="number of bins for each axis", metavar=("X_BINS", "Y_BINS"))
    parser_plrmode.add_argument("-xa", "--xabs", action="store_true", dest="x_use_abs_val", default=False, help="use the absolute value of the x-axis dataset")
    parser_plrmode.add_argument("-ya", "--yabs", action="store_true", dest="y_use_abs_val", default=False, help="use the absolute value of the y-axis dataset")
    parser_plrmode.add_argument("-c", "--cap-loglike", type=float, action="store", dest="cap_loglike_val", default=None, help="cap the ln(L) at the given value", metavar="CAP_VAL")
    parser_plrmode.add_argument("-g", "--gray", action="store_true", dest="use_grayscale", default=False, help="grayscale plot")
    parser_plrmode.add_argument("-wb", "--white-bg", action="store_true", dest="use_white_bg", default=False, help="white background")

    # Parse the arguments and run the function for the chosen mode
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
