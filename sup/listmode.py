# -*- coding: utf-8 -*-
import os
from sup.utils import (
    check_file_type, get_dataset_names_hdf5, get_dataset_names_txt
    )

def run(args):
    """The main function for the 'list' run mode.

    This function reads the input file and outputs an enumerated list of all
    the datasets contained in the file.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    """

    dset_names = []
    file_type = check_file_type(args.input_file)

    if file_type == "text":
        print("Reading " + args.input_file + " as a text file")
        print()
        dset_names = get_dataset_names_txt(args.input_file)

    elif file_type == "hdf5":
        print("Reading " + args.input_file + " as an HDF5 file")
        print()
        import h5py
        f = h5py.File(args.input_file, 'r')
        dset_names = get_dataset_names_hdf5(f)
        f.close()

    else:
        raise ValueError("Unrecognized file_type: '{}'".format(file_type))

    # Print the dataset names
    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dset_names):
        print(i, " \t ", dset_name, sep='')

    return
