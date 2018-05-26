import argparse
import bark
import os
import pandas as pd
import subprocess
import sys

def concatenate_datasets(sampled, events, out, entry_list):
    if sys.platform == 'win32':
        cat_cmd = ['copy']
    else: # OS X, linux, unix, cygwin. others without cat can open an issue
        cat_cmd = ['cat']
    sampled_out = os.path.splitext(out)[0] + '.dat'
    event_out = os.path.splitext(out)[0] + '.csv'
    df_list = []
    offset = 0
    eds_metadata = None
    sds_metadata = None
    # obviously this will die if any entry lacks one of the datasets
    ds_iterator = ((bark.read_sampled(os.path.join(entry, sampled)),
                    bark.read_events(os.path.join(entry, events)))
                   for entry in entry_list)
    for sds,eds in ds_iterator:
        if sds_metadata is None:
            sds_metadata = sds.attrs
        if sds_metadata['sampling_rate'] != sds.sampling_rate:
            raise ValueError('cannot concatenate sampled datasets with different sampling rates')
        if len(sds_metadata['columns']) != sds.data.shape[1]:
            raise ValueError('cannot concatenate sampled datasets with different numbers of columns')
        if sds_metadata['dtype'] != sds.attrs['dtype']:
            raise ValueError('cannot concatenate sampled datasets with different dtypes')
        if eds_metadata is None:
            eds_metadata = eds.attrs
        for col,info in eds.attrs['columns'].items():
            if col not in eds_metadata['columns']:
                eds_metadata['columns'][col] = info
            elif eds_metadata['columns'][col] != info:
                raise ValueError('cannot concatenate event datasets with conflicting column metadata')
        cat_cmd.append(sds.path)
        if sys.platform == 'win32':
            cat_cmd.append('+')
        eds.data['start'] += offset
        if 'stop' in eds.data.columns:
            eds.data['stop'] += offset
        else: # easier to do this than handle the NaNs later
            eds.data['stop'] = eds.data['start']
        df_list.append(eds.data)
        offset += sds.data.shape[0] / sds.sampling_rate
    new_eds = bark.write_events(event_out,
                                pd.concat(df_list, ignore_index=True),
                                **eds_metadata)
    if sys.platform == 'win32':
        cat_cmd.pop() # remove the last '+'
        cat_cmd.extend([sampled_out, '/B'])
    else:
        cat_cmd.extend(['>', sampled_out])
    subprocess.run(cat_cmd)
    bark.write_metadata(sampled_out, **sds_metadata)

def _parse_args(raw_args):
    desc = 'Concatenate sampled and event datasets in a set of entries'
    p = argparse.ArgumentParser(description=desc)
    p.add_argument('sampled_ds', help='name of sampled dataset')
    p.add_argument('event_ds', help='name of event dataset')
    p.add_argument('out', help='name of output datasets (shared) (extension will be ignored)'))
    p.add_argument('entry', help='entries to search for datasets', nargs='+')
    return p.parse_args(raw_args)

def _main():
    p = _parse_args(sys.argv[1:])
    concatenate_datasets(p.sampled_ds, p.event_ds, p.out, p.entry)

if __name__ == '__main__':
    _main()
