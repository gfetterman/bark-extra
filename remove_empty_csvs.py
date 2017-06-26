import os
import bark
import numpy as np
def main(csvfiles, min_lines, ignore_syllable=None, verbose=True):
    for csvfile in csvfiles:
        dset = bark.read_events(csvfile)
        if ignore_syllable:
            dset.data = dset.data[np.logical_not(dset.data.name.str.match(ignore_syllable))]
        if len(dset.data) <= min_lines:
            if verbose:
                print('deleting', csvfile)
            os.remove(csvfile)




def _run():
    ''' Function for getting commandline args.'''
    import argparse

    p = argparse.ArgumentParser(description='''
    Remove intro notes that are too far from the actual song
    ''')
    p.add_argument('csv', nargs='+', help='name of the event dataset with labels')
    p.add_argument('--min-lines',
            help='minium number of lines, EXCLUDING the header. default: 0',
                   type=int, default=0)
    p.add_argument('--ignore-syllable', default=None,
            help='ignore a particular syllable, ie lines with this syllable will not count')
    args = p.parse_args()
    main(args.csv, args.min_lines, args.ignore_syllable)


if __name__ == '__main__':
    _run()
