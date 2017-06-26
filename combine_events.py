import bark
import pandas as pd

def combine_dsets(events, events2, overwrite):
    if overwrite:
        i = 0
        while i < len(events):
            e1 = events[i]
            marked_for_del = False
            for e2 in events2:
                if e1['start'] > e2['start'] and e1['start'] < e2['stop']:
                    marked_for_del = True
                elif e1['stop'] > e2['start'] and e1['stop'] < e2['stop']:
                    marked_for_del = True
            if marked_for_del:
                #print('not valid! ', events[i])
                del events[i]
                i -= 1
            i += 1
    events.extend(events2)
    return events

def main(csv1, csv2, outfile, overwrite, nocomplain):
    event_dset1 = bark.read_events(csv1)
    try:
        event_dset2 = bark.read_events(csv2)
    except OSError as e:
        if nocomplain:
            print('no {}... skipping'.format(csv2))
            bark.write_events(outfile, event_dset1.data, **event_dset1.attrs)
            return
        else:
            raise e
    event_list1 = event_dset1.data.to_dict('records')
    event_list2 = event_dset2.data.to_dict('records')
    filtered_event_list = combine_dsets(event_list1, event_list2, overwrite)
    newdf = pd.DataFrame.from_records(filtered_event_list)
    if len(newdf) > 0:
        newdf.sort_values('start', axis=0, inplace=True)
    bark.write_events(outfile,  newdf, **event_dset1.attrs)


def _run():
    ''' Function for getting commandline args.'''
    import argparse

    p = argparse.ArgumentParser(description='''
    Combine two events datasets.
    ''')
    p.add_argument('csv1', help='name of first event dataset')
    p.add_argument('csv2', help='name of second event dataset')
    p.add_argument('out', help='name of output event dataset')
    p.add_argument('--overwrite',
                   help='if events in the first dataset overlap events in the second, they are removed',
                   action='store_true')
    p.add_argument('--nocomplain',
                   help='run even if second dataset does not exist',
                   action='store_true')
    args = p.parse_args()
    main(args.csv1, args.csv2, args.out, args.overwrite, args.nocomplain)


if __name__ == '__main__':
    _run()
