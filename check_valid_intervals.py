import sys
import pandas
import argparse

def check_start_stop(fname, inplace=False):
    df = pandas.read_csv(fname)
    record_dicts = df.to_dict('records')
    if 'stop' not in record_dicts[0]:
        return
    for i, r in enumerate(record_dicts):
        if r['stop'] < r['start']:
            print("{} line {}: {}".format(fname, i + 1, r))
            r['start'], r['stop'] = r['stop'], r['start']
    if inplace:
        pandas.DataFrame(record_dicts).to_csv(fname, index=False)

def get_args():
    p = argparse.ArgumentParser(description="""
    make sure stop is after start
    """)
    p.add_argument("csv", help="CSV files", nargs="+")
    p.add_argument("--inplace", help="fix csvs in place", action="store_true")
    args = p.parse_args()
    return args.csv, args.inplace

if __name__ == '__main__':
    csvs, inplace = get_args()
    for fname in csvs:
        check_start_stop(fname, inplace)
