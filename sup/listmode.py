import os
from sup.utils import get_dataset_names

def run(args):

    filename_without_extension, file_extension = os.path.splitext(args.input_file)

    if file_extension in ['.hdf5', '.h5', '.he5']:
        print("Reading " + args.input_file + " as an HDF5 file")
        print()
        run_hdf5(args)

    else:
        print("Reading " + args.input_file + " as a text file")
        print()
        run_txt(args)

    return



def run_hdf5(args):

    import h5py

    f = h5py.File(args.input_file, 'r')
    dset_names = get_dataset_names(f)
    f.close()

    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dset_names):
        print(i, " \t ", dset_name, sep='')

    return



def run_txt(args):

    from io import StringIO 
    import numpy as np

    # To avoid reading the entire file just to list the dataset names
    # we'll use a StringIO file-like object constructed from the first
    # interesting line in the file.

    comments = '#'

    # Let's find the first non-empty comment line, which we require 
    # should contain the column names.
    firstline = ''
    with open(args.input_file) as f:
        templine = ''
        for line in f:
            templine = line.lstrip().rstrip()
            if not ((templine == '') or (templine == comments)):
                break
        firstline = templine

    use_names = True
    # If firstline is not a header with column names, we have to create
    # a list of names based on the number of columns we detect from firstline.
    if not firstline.startswith(comments):
        n_cols = len(firstline.replace(',', ' ').split())
        use_names = ['dataset' + str(i) for i in range(n_cols)]


    stringIO_file = StringIO(firstline)
    dsets = np.genfromtxt(stringIO_file, names=use_names, comments=comments)

    # dsets = np.genfromtxt(args.input_file, delimiter=',', names=True)    

    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dsets.dtype.names):
        print(i, " \t ", dset_name, sep='')

    return