# -*- coding: utf-8 -*-
import os
from sup.utils import (
    check_file_type, get_dataset_names_hdf5, get_dataset_names_txt,
    get_all_column_dataset_names_sql
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
    
    elif file_type == "sql":
        print("Reading " + args.input_file + " as an SQL (SQLite) file")
        print()
        dset_names = get_all_column_dataset_names_sql(args.input_file)

    else:
        # This case should ideally not be reached if check_file_type is comprehensive
        # and covers all types it can return.
        raise ValueError("Unrecognized file_type: '{}' returned by check_file_type.".format(file_type))

    # Print the dataset names
    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dset_names):
        print(i, " \t ", dset_name, sep='')

    return
