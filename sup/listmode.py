# -*- coding: utf-8 -*-
import os
import sys
from sup.utils import (
    check_file_type, get_dataset_names_hdf5, get_dataset_names_txt,
    get_dataset_names_csv, get_dataset_names_json, SupRuntimeError, error_prefix
    )

def run(args):
    """The main function for the 'list' run mode.

    This function reads the input file or stream and outputs an enumerated list 
    of all the datasets contained.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    """
    dset_names = []
    
    if args.input_file == '-':
        if not args.stdin_format:
            # This case should ideally be caught by argparser in sup.py,
            # but as a safeguard:
            print(f"{error_prefix} --stdin-format is required when reading from stdin for list mode.")
            return 1 # Or raise SupRuntimeError
            
        print(f"Reading from stdin as {args.stdin_format}...")
        print()
        if args.stdin_format == 'txt':
            dset_names, _ = get_dataset_names_txt(sys.stdin)
        elif args.stdin_format == 'csv':
            dset_names, _ = get_dataset_names_csv(sys.stdin)
        elif args.stdin_format == 'hdf5':
            # As per previous logic, HDF5 from stdin is not supported.
            print(f"{error_prefix} Listing datasets from HDF5 via stdin is not supported.")
            return 1 # Or raise SupRuntimeError
        else:
            # Should be caught by choices in argparse
            print(f"{error_prefix} Unknown stdin format: {args.stdin_format}")
            return 1 # Or raise SupRuntimeError
            
    else: # It's a file path
        file_type = check_file_type(args.input_file)
        if file_type == "text":
            print("Reading " + args.input_file + " as a text file")
            print()
            dset_names, _ = get_dataset_names_txt(args.input_file) 

        elif file_type == "csv":
            print("Reading " + args.input_file + " as a CSV file")
            print()
            dset_names, _ = get_dataset_names_csv(args.input_file) 

        elif file_type == "json":
            print("Reading " + args.input_file + " as a JSON file")
            print()
            dset_names, _ = get_dataset_names_json(args.input_file) 
                                                # We only need names for listmode
        elif file_type == "hdf5":
            print("Reading " + args.input_file + " as an HDF5 file")
            print()
            import h5py # Keep h5py import local as it's only for HDF5
            try:
                with h5py.File(args.input_file, 'r') as f:
                    dset_names = get_dataset_names_hdf5(f)
            except OSError as e:
                print(f"{error_prefix} Could not read HDF5 file: {args.input_file}. Error: {e}")
                return 1 # Or raise SupRuntimeError
        else:
            # Should be caught by check_file_type if it's exhaustive or raises error
            print(f"{error_prefix} Unrecognized file_type: '{file_type}' for file {args.input_file}")
            return 1 # Or raise SupRuntimeError

    # Print the dataset names
    if not dset_names:
        print("No datasets found or error in reading.")
        return # Or return appropriate error code if not already done
        
    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dset_names):
        print(i, " \t ", dset_name, sep='')

    return
