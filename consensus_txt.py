import argparse
import os
import pandas
import progressbar
from collections import Counter

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


def most_common_text(input_file, output_folder, show_score=False, replace_arrow=False):
    reducer_table = pandas.read_csv(input_file)
    frames = sorted([c for c in reducer_table.columns if 'data.frame' in c])
    edx = reducer_table.reducer_key == 'ext'
    counter = 0
    pbar = progressbar.ProgressBar(widgets=widgets, max_value=edx.sum())
    pbar.start()
    for idx, reduction in reducer_table[edx].iterrows():
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
                    if show_score:
                        consensus = ' [{0:.3}/{1}]'.format(l['consensus_score'], l['number_views'])
                    else:
                        consensus = ''
                    lines.append(' '.join(most_common) + consensus)
                pages.append('\n'.join(lines))
        transcription = '\n\n'.join(pages)
        with open('{0}/{1}.txt'.format(output_folder, reduction.subject_id), 'w') as file_out:
            file_out.write(transcription)
        counter += 1
        pbar.update(counter)
    pbar.finish()


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
    args = parser.parse_args()
    most_common_text(args.input_file, args.output_folder, show_score=args.show_score, replace_arrow=args.replace_arrow)
