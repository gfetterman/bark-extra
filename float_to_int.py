import argparse
import bark
import numpy
import sys
import subprocess

parser = argparse.ArgumentParser(description='Converts jill outputs to int16')
parser.add_argument('input', help='Bark dataset input filename')
parser.add_argument('output', help='output filename')
args = parser.parse_args()

attrs = bark.read_metadata(args.input)
sr = str(attrs['sampling_rate'])
ch = str(len(attrs['columns']))
enc = 'float' # jill output
bd = '32' # jill output

dt = numpy.dtype(attrs['dtype'])
if dt.byteorder == '<':
    order = 'little'
elif dt.byteorder == '>':
    order = 'big'
elif dt.byteorder == '=': # native
    order = sys.byteorder
else:
    raise valueError('unrecognized endianness: ' + dt.byteorder)

new_enc = 'signed-integer'
new_bd = '16'

sox_cmd = ['sox', '-r', sr, '-c', ch, '-b', bd, '-e', enc,
           '--endian', order, '-t', 'raw', args.input,
           '-b', new_bd, '-e', new_enc, '-t', 'raw', args.output]
subprocess.run(sox_cmd)

