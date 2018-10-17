import argparse
import bark
import bark.tools.barkutils
import os
import sys
import textwrap

DAT_SPLIT_SUFFIX = '-chunk-{}'
BARK_META_SUFFIX = '.meta.yaml'

def many_splits(dat_file, split_points):
    # WARNING: this functionality is distinctly not thread-safe
    curr_file = dat_file
    for idx, sp in enumerate(reversed(split_points)):
        print('split point #{}: {}'.format(len(split_points) - idx, sp))
        print('current file to split from: {}'.format(curr_file))
        calved_file = os.path.splitext(curr_file)[0] + DAT_SPLIT_SUFFIX.format(1) + os.path.splitext(curr_file)[1]
        calved_file_new_name = os.path.splitext(dat_file)[0] + DAT_SPLIT_SUFFIX.format(len(split_points) - idx) + os.path.splitext(dat_file)[1]
        print('calved_file: {}'.format(calved_file))
        print('new name for calved file: {}'.format(calved_file_new_name))
        bark.tools.barkutils.datchunk(curr_file, sp, use_seconds=False, one_cut=True)
        if curr_file != dat_file:
            os.remove(curr_file)
            os.remove(curr_file + BARK_META_SUFFIX)
        curr_file = os.path.splitext(curr_file)[0] + DAT_SPLIT_SUFFIX.format(0) + os.path.splitext(curr_file)[1]
        os.rename(calved_file, calved_file_new_name)
        os.rename(calved_file + BARK_META_SUFFIX, calved_file_new_name + BARK_META_SUFFIX)
    os.rename(curr_file, os.path.splitext(dat_file)[0] + DAT_SPLIT_SUFFIX.format(0) + os.path.splitext(dat_file)[1])
    os.rename(curr_file + BARK_META_SUFFIX, os.path.splitext(dat_file)[0] + DAT_SPLIT_SUFFIX.format(0) + os.path.splitext(dat_file)[1] + BARK_META_SUFFIX)

def _transform_check_split_points(dat_file, split_points, seconds):
    sorted_points = sorted(split_points)
    if sorted_points != split_points:
        print('Warning: split points were out-of-order. They have been sorted.')
        split_points = sorted_points
    sampled_ds = bark.read_sampled(dat_file)
    file_length_samples = sampled_ds.data.shape[0]
    if seconds:
        split_points = [int(sp * sampled_ds.sampling_rate) for sp in split_points]
    else:
        split_points = [int(sp) for sp in split_points]
    for sp in split_points:
        if sp > file_length_samples:
            msg = 'cannot split at sample {} - file only contains {} samples'.format(sp, file_length_samples)
            raise ValueError(msg)
    return split_points

def _parse_args(raw_args):
    desc = 'Split a .dat file at given points'
    epi = "Split points will be sorted before splitting. Split points must be within file."
    parser = argparse.ArgumentParser(description=desc, epilog=epi)
    parser.add_argument('--seconds', help='specify split points in seconds (otherwise, samples)', action='store_true')
    parser.add_argument('dat', help='dat file to split')
    parser.add_argument('split_point', help='split point (relative to start of file) (can provide arbitrarily many)', nargs='+', type=float)
    return parser.parse_args(raw_args)

def _main():
    pargs = _parse_args(sys.argv[1:])
    split_points = _transform_check_split_points(pargs.dat, pargs.split_point, pargs.seconds)
    many_splits(pargs.dat, split_points)

if __name__ == '__main__':
    _main()

