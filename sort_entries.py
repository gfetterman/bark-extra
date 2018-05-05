import argparse
import bark
import datetime
import math
import os
import sys

ENTRY_PREFIX = 'jrecord_'
MIN_PADDING = 4
TEMP_SUFFIX = 'a'
ROOT_PATTERN = '{birdname}_{datestring}'
DATE_PATTERN = '%y%m%d'
DATE_PATTERN_LEN = 6

def parse_args(raw_args):
    desc = 'Re-allocates entries among one or more Bark roots by date and time.'
    epi = 'Any new Bark roots will be created as children of the parent directory of the first root specified.'
    parser = argparse.ArgumentParser(description=desc, epilog=epi)
    parser.add_argument('-t', '--time', default='00:00',
                        help='24-hr time at which to split days (format: HH:MM) (default: 00:00)')
    parser.add_argument('-f', '--freeze', action='store_true',
                        help='out-of-place entries will be left as-is if moving would create a new root')
    parser.add_argument('roots', nargs='+',
                        help='one or more Bark roots containing entries to re-arrange')
    return parser.parse_args(raw_args)

def reallocate_entries(input_roots, split_time, new_root_prefix, freeze):
    all_roots = []
    for r in input_roots:
        all_roots.append(r)
        root = bark.read_root(r)
        for e in root.entries:
            entry = root.entries[e]
            if not this_root_correct(r, entry):
                cr = correct_root(entry, new_root_prefix)
                if os.path.exists(cr):
                    move_entry(entry.path, os.path.join(cr, os.path.split(entry.path)[-1]))
                elif not freeze:
                    os.mkdir(cr)
                    all_roots.append(cr)
                    move_entry(entry.path, os.path.join(cr, os.path.split(entry.path)[-1]))
                # else do nothing - user doesn't want new roots created
            # else do nothing - it's in the right place
    return all_roots

def this_root_correct(root, entry):
    root_date = datetime.datetime.strptime(root[-DATE_PATTERN_LEN:], DATE_PATTERN).date()
    entry_date = entry.timestamp.date()
    return entry_date == root_date

def correct_root(entry, new_root_prefix):
    return new_root_prefix + entry.timestamp.strftime(DATE_PATTERN)

def move_entry(old_path, new_path):
    while os.path.exists(new_path):
        new_path += TEMP_SUFFIX
    os.rename(old_path, new_path)

def temp_shift(root):
    all_entries = bark.read_root(root).entries
    for e in all_entries:
        entry = all_entries[e]
        move_entry(entry.path, entry.path) # so every entry gets at least one TEMP_SUFFIX appended

def movesort_entries(root):
    temp_shift(root)
    r = bark.read_root(root)
    sorted_entries = sorted([r.entries[e] for e in r.entries], key=lambda x: x.timestamp)
    num_entries = len(sorted_entries)
    if num_entries:
        padding = max(MIN_PADDING, int(math.floor(math.log(num_entries) / math.log(10))) + 1)
    else:
        padding = 1
    name_format_str = '{pre}{num:0{pad}}'
    for idx,entry in enumerate(sorted_entries):
        new_path = os.path.join(r.path, name_format_str.format(pre=ENTRY_PREFIX, num=idx, pad=padding))
        move_entry(entry.path, new_path)

def _main():
    pargs = parse_args(sys.argv[1:])
    new_root_parent = os.path.split(pargs.roots[0])[0]
    new_root_prefix = pargs.roots[0][:-6] # assumes, e.g., black205_170910, so prefix is black205_
    split_time = datetime.datetime.strptime(pargs.time, '%H:%M').time()
    all_roots = reallocate_entries(pargs.roots, split_time, new_root_prefix, pargs.freeze)
    for root in all_roots:
        movesort_entries(root)

if __name__ == '__main__':
    _main()
