import argparse
import os
import pandas
import progressbar
from collections import Counter, OrderedDict

widgets = [
    'Processing: ',
    progressbar.Percentage(),
    ' ', progressbar.Bar(),
    ' ', progressbar.ETA()
]


def non_blank_counter(x):
    c = Counter(x)
    if '' in c:
        del(c[''])
    return c


def most_common_text(input_file, output_folder, show_score=False, replace_arrow=False, reducer_key=None, strip_sw=False, csv=None, metadata=None):
    reducer_table = pandas.read_csv(input_file)
    frames = sorted([c for c in reducer_table.columns if 'data.frame' in c])
    if reducer_key is not None:
        edx = reducer_table.reducer_key == reducer_key
        table_to_loop = reducer_table[edx]
    else:
        table_to_loop = reducer_table
    if csv is not None:
        csv_output = OrderedDict([
            ('zooniverse_subject_id', []),
            ('text', []),
            ('consensus_score', []),
            ('number_views', [])
        ])
        if metadata is not None:
            subjects = pandas.read_csv(metadata)
            subjects.metadata = subjects.metadata.apply(eval)
            for key in subjects.iloc[0].metadata.keys():
                csv_output[key] = []
    counter = 0
    pbar = progressbar.ProgressBar(widgets=widgets, max_value=len(table_to_loop))
    pbar.start()
    for idx, reduction in table_to_loop.iterrows():
        if csv is not None:
            consensus_score = []
            number_views = []
        pages = []
        for frame in frames:
            if not pandas.isnull(reduction[frame]):
                if replace_arrow:
                    data = eval(reduction[frame].replace('=>', ':'))
                else:
                    data = eval(reduction[frame])
                lines = []
                for l in data:
                    text_counter = [non_blank_counter(t) for t in l['clusters_text']]
                    most_common = [tc.most_common()[0][0] for tc in text_counter if len(tc) > 0]
                    if csv is not None:
                        consensus_score.append(l['consensus_score'])
                        number_views.append(l['number_views'])
                        consensus = ''
                    elif show_score:
                        consensus = ' [{0:.3}/{1}]'.format(l['consensus_score'], l['number_views'])
                    else:
                        consensus = ''
                    lines.append(' '.join(most_common) + consensus)
                pages.append('\n'.join(lines))
        transcription = '\n\n'.join(pages)
        if strip_sw:
            transcription = transcription.replace('<sw-', '<')
            transcription = transcription.replace('</sw-', '</')
        if csv is not None:
            csv_output['zooniverse_subject_id'].append(reduction.subject_id)
            csv_output['text'].append(transcription)
            csv_output['consensus_score'].append(consensus_score)
            csv_output['number_views'].append(number_views)
            if metadata is not None:
                idx = (subjects.subject_id == reduction.subject_id) & (subjects.workflow_id == reduction.workflow_id)
                for key, value in subjects[idx].iloc[0].metadata.items():
                    csv_output[key].append(value)
        with open('{0}/{1}.txt'.format(output_folder, reduction.subject_id), 'w') as file_out:
            file_out.write(transcription)
        counter += 1
        pbar.update(counter)
    pbar.finish()
    if csv is not None:
        pandas.DataFrame(csv_output).to_csv('{0}/{1}.csv'.format(output_folder, csv), index=False)


def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Turn caesar reductions from ASM into consensus text files')
    parser.add_argument('input_file', type=argparse.FileType('r'), help='The reduction export from caesar for the workflow')
    parser.add_argument('output_folder', type=is_dir, help='The folder to save the `.txt` files to')
    parser.add_argument('-s', '--show-score', action='store_true', help='Show consensus scores for each line of text')
    parser.add_argument('-r', '--replace-arrow', action='store_true', help='Replace `=>` with `:` in csv dump before processing (only needed for old Caesar data dumps)')
    parser.add_argument('-k', '--reducer-key', default=None, help='The reducer key to use, if left blank no key is used (useful for data processed offline)')
    parser.add_argument('--strip-sw', action='store_true', help='Strip "sw-" for tag names')
    parser.add_argument('-c', '--csv', default=None, help='Make a `.csv` file with this name contaning all the transcriptions')
    parser.add_argument('-m', '--metadata', default=None, help='The `metadata` column of this subjects `csv` file will be unpaced into the ouput `csv` table')
    args = parser.parse_args()
    most_common_text(
        args.input_file,
        args.output_folder,
        show_score=args.show_score,
        replace_arrow=args.replace_arrow,
        reducer_key=args.reducer_key,
        strip_sw=args.strip_sw,
        csv=args.csv,
        metadata=args.metadata
    )
