import argparse
import bark
import os
import shutil
import sys

def turn_red(string):
    return '\x1b[{}m{}\x1b[0m'.format('31', string)

def _parse_args(raw_args):
    desc = 'Delete Entries for which the given event dataset is empty.'
    epi = 'This operation is destructive. Be careful!'
    if sys.stdout.isatty():
        epi = turn_red(epi)
    parser = argparse.ArgumentParser(description=desc, epilog=epi)
    parser.add_argument('-v', '--verbose', help='increase verbosity',
                        action='store_true')
    parser.add_argument('root', help='head of Bark tree (Root)')
    parser.add_argument('event_dataset', help='name of event dataset to use')
    return parser.parse_args(raw_args)

def winnow_entries(root, event_ds, verbose=False):
    """Removes all entries in a Bark root with empty event_ds.
    
       root      --  string; path to Bark root
       event_ds  --  string; name of Bark event dataset
       verbose   --  boolean"""
    root = bark.read_root(root)
    removals = []
    for entry_name in root.entries:
        entry = root.entries[entry_name]
        if event_ds not in entry.datasets:
            if verbose:
                print(event_ds + ' not in ' + entry_name)
            # and do nothing
        else:
            if ('dtype' not in entry.datasets[event_ds].attrs and
                entry.datasets[event_ds].data.empty):
                removals.append(entry_name)
            elif verbose:
                print('Leaving Entry ' + entry_name)
    removals = [root.entries[e].path for e in removals]
    # memmaps play merry hell with shutil.rmtree,
    # so we want to close them out first
    del root, entry
    for entry_path in removals:
        shutil.rmtree(entry_path)
        if verbose:
            print('Removing Entry ' + os.path.split(entry_path)[-1])
    return removals

def _main():
    args = _parse_args(sys.argv[1:])
    _ = winnow_entries(args.root, args.event_dataset, args.verbose)

if __name__ == '__main__':
    _main()
