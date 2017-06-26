import bark
import pandas as pd

def remove_intro_notes(events, min_dist, song_notes, intro_note):
    i = 0
    while i < len(events):
        if events[i]['name'] != intro_note:
            i += 1
            continue
        intro_time = events[i]['start']
        j = i
        valid = False
        while (j < len(events)) and (events[j]['start'] - events[i]['start'] < min_dist):
            if events[j]['name'] in song_notes:
                valid = True
            j += 1
        if not valid:
            #print('not valid! ', events[i])
            del events[i]
            i -= 1
        i += 1
    return events

def main(csvfile, outfile, min_dist, song_notes, intro_note='i'):
    event_dset = bark.read_events(csvfile)
    event_list = event_dset.data.to_dict('records')
    filtered_event_list = remove_intro_notes(event_list, min_dist, song_notes, intro_note)
    bark.write_events(outfile, pd.DataFrame(filtered_event_list), **event_dset.attrs)


def _run():
    ''' Function for getting commandline args.'''
    import argparse

    p = argparse.ArgumentParser(description='''
    Remove intro notes that are too far from the actual song
    ''')
    p.add_argument('csv', help='name of the event dataset with labels')
    p.add_argument('out', help='name of output event dataset')
    p.add_argument('--min',
                   help='minium distance in seconds between intro note and a song note, default 1 second',
                   type=float, default=1.0)
    p.add_argument('-n',
                   '--song-notes',
                   nargs='+',
                   help='notes in the song, default: a b',
                   default=('a', 'b'))
    p.add_argument('-i',
                   '--intro-note',
                   nargs='+',
                   help='name of intro note, default: i',
                   default='i')
    args = p.parse_args()
    main(args.csv, args.out, args.min, args.song_notes)


if __name__ == '__main__':
    _run()
