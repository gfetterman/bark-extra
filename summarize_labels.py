import argparse
import bark
import collections
import sys

EVENT_FILE = 'blv_out.csv'

def _parse_args(raw_args):
    desc = 'Pool labels from label files in all entries in a given root.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('root', help='Bark root')
    parser.add_argument('-e', '--events', nargs='+', default=[EVENT_FILE],
                        help='event files to read (default: {})'.format(EVENT_FILE))
    return parser.parse_args(raw_args)

def pool_labels(root_path, event_files):
    root = bark.read_root(root_path)
    label_dict = collections.Counter()
    for e in root.entries:
        entry = root.entries[e]
        for ef in event_files:
            if ef in entry:
                label_dict.update(entry.datasets[ef].data.name)
    return label_dict

def print_counter(counter):
    for item in counter:
        print('{}: {}'.format(item, counter[item]))

def _main():
    pargs = _parse_args(sys.argv[1:])
    label_dict = pool_labels(pargs.root, pargs.events)
    print_counter(label_dict)

if __name__ == '__main__':
    _main()
