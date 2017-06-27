import argparse
import bark
import collections
import sys

def _parse_args(arg_list):
    desc = 'Generate a readout of entries and hours.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('root', help='Bark root')
    return parser.parse_args(arg_list)

HourEntries = collections.namedtuple('HourEntries',
                                     ['hour', 'first', 'entries'])

def pull_times(root):
    r = bark.read_root(root)
    grouped_entries = collections.defaultdict(list)
    for ename in r.entries:
        entry = r.entries[ename]
        hour = entry.timestamp.replace(minute=0, second=0, microsecond=0,
                                       tzinfo=None)
        grouped_entries[hour].append(entry)
    times = [HourEntries(h,
                         min(elist, key=lambda e: e.timestamp),
                         elist)
             for h,elist in sorted(grouped_entries.items())]
    return times

def print_times(times):
    for t in times:
        line = (t.hour.isoformat(sep=' ', timespec='minutes') + ': ' + 
                str(len(t.entries)) + ' entries, starting with ' +
                t.first.name)
        print(line)

if __name__ == '__main__':
    parsed_args = _parse_args(sys.argv[1:])
    times = pull_times(parsed_args.root)
    print_times(times)
