import argparse
import bark
import numpy as np
import os
import pandas
import scipy.io.wavfile
import sys

THRESHOLD = -20000.

def _parse_args(raw_args):
    desc = 'Combine jill triggers and jstim output to make a stimulus time .csv'
    epi = 'Entry metadata must include jstim .log file and stimulus .wav file locations'
    parser = argparse.ArgumentParser(description=desc, epilog=epi)
    dflt = 'stim_times.csv'
    parser.add_argument('-o', '--out', help='output file (default: {})'.format(dflt), default=dflt)
    parser.add_argument('entry', help='Bark entry')
    parser.add_argument('adc', help='board ADC filename')
    return parser.parse_args(raw_args)

def gen_stim_times(entry_fn, adc_fn, out_fn):
    entry = bark.read_entry(entry_fn)
    
    # pull starts from ADC trigger channel and convert to seconds
    above_thresh = (entry[adc_fn].data[:,0] >= THRESHOLD).astype(int)
    starts = (np.nonzero(np.diff(above_thresh) > 0)[0]) / entry[adc_fn].attrs['sampling_rate']
    
    # pull stimulus order and names from jstim log
    try:
        with open(entry.attrs['jstim_log'], 'r') as logfile:
            stim_name_lines = [line.split()[4] for line in logfile.readlines()
                               if len(line.split()) > 4 and line.split()[2] == 'next']
    except KeyError as exc:
        msg = 'The entry meta.yaml file must contain "jstim_log", a link to the jstim .log file.'
        raise KeyError(msg) from exc
    wav_fns = list(set(stim_name_lines))
    
    # determine stimulus file lengths
    try:
        stim_files = entry.attrs['stim_files']
    except KeyError as exc:
        msg = ('The entry meta.yaml file must contain "stim_files", a dict of stimulus ' + 
               'names in the jstim log and their file paths.')
        raise KeyError(msg) from exc
    try:
        wav_details = {fn: scipy.io.wavfile.read(stim_files[fn]) for fn in wav_fns}
    except KeyError as exc:
        msg = 'The stimulus names in "stim_files" do not match those in the jstim log.'
        raise KeyError(msg) from exc
    wav_lengths = {fn: (len(data) / sr) for fn,(sr,data) in wav_details.items()}
    
    # determine stimulus intervals
    wav_indices = {fn: np.nonzero(np.array(stim_name_lines) == fn)[0] for fn in wav_fns}
    stim_times = set()
    for fn in wav_fns:
        stim_times.update({(starts[idx], (starts[idx] + wav_lengths[fn]), fn)
                          for idx in wav_indices[fn]})
    stim_times = sorted(list(stim_times), key=lambda x: x[0])
    
    # write stimulus intervals to Bark event dataset
    return bark.write_events(os.path.join(entry_fn, out_fn),
                             pandas.DataFrame({'start': [e[0] for e in stim_times],
                                               'stop': [e[1] for e in stim_times],
                                               'name': [e[2] for e in stim_times]}),
                             **{'columns': {'name': {'units': None},
                                            'start': {'units': 's'},
                                            'stop': {'units': 's'}},
                                           'datatype': 2001})
    

def _main():
    parsed_args = _parse_args(sys.argv[1:])
    _ = gen_stim_times(parsed_args.entry, parsed_args.adc, parsed_args.out)

if __name__ == '__main__':
    _main()