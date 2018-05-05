import argparse
import bark
import os

ENTRY_PREFIX = 'jrecord_'

desc = 'Lists entries in a given Bark root which contain a given file.'
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('root', help='Bark root to work on')
parser.add_argument('file', help='file to search for')
parser.add_argument('-p', '--prefix', help='Bark entry prefix')
pargs = parser.parse_args()

entries = bark.read_root(pargs.root).entries
has_file = {ename for ename in entries if os.path.exists(os.path.join(entries[ename].path, pargs.file))}
not_has_file = set(entries.keys()) - has_file

def group_entry_names(entries, prefix=ENTRY_PREFIX):
    for e in entries:
        if not e.startswith(prefix):
            raise ValueError('not every entry begins with "{}"'.format(prefix))
    if not entries:
        return []
    else:
        sorted_entries = sorted(entries)
        groups = [[sorted_entries[0]]]
        for e in sorted_entries[1:]:
            if int(e[len(prefix):]) == int(groups[-1][-1][len(prefix):]) + 1:
                groups[-1].append(e)
            else:
                groups.append([e])
        return groups

def print_grouped_entries(grouped_entries, prefix=ENTRY_PREFIX):
    if not grouped_entries:
        print('  [No entries]')
    else:
        for group in grouped_entries:
            if len(group) == 1:
                print('  ' + group[0])
            else:
                initial = group[0][len(prefix):]
                final = group[-1][len(prefix):]
                print('  {}{} - {}'.format(prefix, initial, final))

print('Entries containing {} ({} total; {:.0%}):'.format(pargs.file, len(has_file), len(has_file) / len(entries)))
print_grouped_entries(group_entry_names(has_file, pargs.prefix), pargs.prefix)

print('Entries not containing {} ({} total; {:.0%}):'.format(pargs.file, len(not_has_file), len(not_has_file) / len(entries)))
print_grouped_entries(group_entry_names(not_has_file, pargs.prefix), pargs.prefix)
