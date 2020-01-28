import argparse
import os
import pandas
import progressbar
import json
from collections import OrderedDict
from panoptes_aggregation.csv_utils import unflatten_data
from panoptes_aggregation.routes import MyEncoder
from pandas.io.json import json_normalize

widgets = [
    'Processing: ',
    progressbar.Percentage(),
    ' ', progressbar.Bar(),
    ' ', progressbar.ETA()
]


def most_common_text(
    input_file,
    output_folder,
    reducer_key=None,
    strip_sw=False,
    csv=None,
    metadata=None
):
    reducer_table = pandas.read_csv(input_file)
    if reducer_key is not None:
        edx = reducer_table.reducer_key == reducer_key
        table_to_loop = reducer_table[edx]
    else:
        table_to_loop = reducer_table
    subject_csv = []
    if metadata is not None:
        subjects = pandas.read_csv(metadata)
        subjects.metadata = subjects.metadata.apply(eval)
    counter = 0
    pbar = progressbar.ProgressBar(widgets=widgets, max_value=len(table_to_loop))
    pbar.start()
    for idx, reduction in table_to_loop.iterrows():
        page_csv = []
        pages = []
        data = unflatten_data(reduction)
        frames = sorted([k for k in data.keys() if 'frame' in k])
        subject_row = OrderedDict([
            ('zooniverse_subject_id', reduction.subject_id),
            ('number_of_pages', len(frames)),
            ('transcribed_lines', data['transcribed_lines']),
            ('low_consensus_lines', data['low_consensus_lines']),
            ('reducer', data['reducer']),
            ('reducer_paramters', data['parameters'])
        ])
        if metadata is not None:
            idx = (subjects.subject_id == reduction.subject_id) & (subjects.workflow_id == reduction.workflow_id)
            subject_row['metadata'] = subjects[idx].iloc[0].metadata
        subject_csv.append(subject_row)
        line_counter = 0
        for frame in frames:
            page_number = int(frame[-1]) + 1
            lines = []
            for line in data[frame]:
                line_counter += 1
                text = line['consensus_text']
                if strip_sw:
                    text = text.replace('<sw-', '<')
                    text = text.replace('</sw-', '</')
                lines.append(text)
                page_row = OrderedDict([
                    ('line_number', line_counter),
                    ('page_number', page_number),
                    ('column_number', line['gutter_label'] + 1),
                    ('text', text),
                    ('slope', line['line_slope']),
                    ('consensus_score', line['consensus_score']),
                    ('number_transcribers', line['number_views']),
                    ('low_consensus', line['low_consensus']),
                    ('start', {
                        'x': line['clusters_x'][0],
                        'y': line['clusters_y'][0],
                    }),
                    ('end', {
                        'x': line['clusters_x'][1],
                        'y': line['clusters_y'][1],
                    }),
                    ('user_ids', line['user_ids'])
                ])
                page_csv.append(page_row)
            pages.append('\n'.join(lines))
        subject_dir = os.path.join(output_folder, str(reduction.subject_id))
        if not os.path.isdir(subject_dir):
            os.mkdir(subject_dir)
        transcription = '\n\n'.join(pages)
        with open(os.path.join(subject_dir, 'transcription.txt'), 'w') as transcription_out:
            transcription_out.write(transcription)
        page_dataframe = json_normalize(page_csv)
        page_csv_out = os.path.join(subject_dir, 'line_metadata.csv')
        page_dataframe.to_csv(page_csv_out, index=False)
        with open(os.path.join(subject_dir, 'aggergation_data.json'), 'w') as json_out:
            json.dump(data, json_out, cls=MyEncoder, indent=2)
        counter += 1
        pbar.update(counter)
    subject_dataframe = json_normalize(subject_csv)
    subject_csv_out = os.path.join(output_folder, 'subject_metadata.csv')
    subject_dataframe.to_csv(subject_csv_out, index=False)
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
    parser.add_argument(
        'input_file',
        type=argparse.FileType('r'),
        help='The reduction export from caesar or offline aggregation for the workflow'
    )
    parser.add_argument(
        'output_folder',
        type=is_dir,
        help='The base folder to output files to'
    )
    parser.add_argument(
        '-k',
        '--reducer-key',
        default=None,
        help='The caesar reducer key for the transcription reducer. This is not needed for aggregation done offline'
    )
    parser.add_argument(
        '--strip-sw',
        action='store_true',
        help='Strip "sw-" for tag names (only used for shakespeares world)'
    )
    parser.add_argument(
        '-m',
        '--metadata',
        default=None,
        help='Path to the panoptes subject data dump `csv` file. When provided the `metadata` column will be included in the output `csv` table'
    )
    args = parser.parse_args()
    most_common_text(
        args.input_file,
        args.output_folder,
        reducer_key=args.reducer_key,
        strip_sw=args.strip_sw,
        metadata=args.metadata
    )
