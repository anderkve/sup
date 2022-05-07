import os
from sup.utils import get_dataset_names_hdf5, get_dataset_names_txt

def run(args):

    filename_without_extension, file_extension = os.path.splitext(args.input_file)

    dset_names = []

    # If a known HDF5 file extension, read as HDF5 file
    if file_extension in ['.hdf5', '.h5', '.he5']:
        print("Reading " + args.input_file + " as an HDF5 file")
        print()
        import h5py
        f = h5py.File(args.input_file, 'r')
        dset_names = get_dataset_names_hdf5(f)
        f.close()
    # All other files are treated as text files
    else:
        print("Reading " + args.input_file + " as a text file")
        print()
        dset_names = get_dataset_names_txt(args.input_file)

    # Print the dataset names
    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dset_names):
        print(i, " \t ", dset_name, sep='')

    return
