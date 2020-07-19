import sys
import h5py
from sup.utils import get_dataset_names

def run(args):

    f = h5py.File(args.input_file, 'r')
    dset_names = get_dataset_names(f)
    f.close()

    print("Index \t Dataset", sep='')
    print("----------------")
    for i, dset_name in enumerate(dset_names):
        print(i, " \t ", dset_name, sep='')

    sys.exit()    
