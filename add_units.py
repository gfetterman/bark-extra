import arf
import argparse
import h5py

parser = argparse.ArgumentParser(description='Adds units')
parser.add_argument('files', nargs='+', help='files to add units to')
args = parser.parse_args()

for f in args.files:
    with arf.open_file(f) as af:
        for ename, entry in af.items():
            if isinstance(entry, h5py.Group):
                raise ValueError('Error: found a group: ' + ename)
            elif isinstance(entry, h5py.Dataset):
                if 'units' in entry.attrs: # presumably a label file
                    entry.attrs['units'] = [b'', b's', b's']
                else: # presumably a time series
                    entry.attrs['units'] = ''
                    
