# ASM consensus text files
This script takes the caesar reduction file for ASM and turns it into a series of text files with the consensus text (one file for each subject).

This is a command line script.  Show the help text with:

```
> python consensus_txt.py -h
usage: consensus_txt.py [-h] [-k REDUCER_KEY] [--strip-sw] [-m METADATA]
                        input_file output_folder

Turn caesar reductions from ASM into consensus text files

positional arguments:
  input_file            The reduction export from caesar or offline
                        aggregation for the workflow
  output_folder         The base folder to output files to

optional arguments:
  -h, --help            show this help message and exit
  -k REDUCER_KEY, --reducer-key REDUCER_KEY
                        The caesar reducer key for the transcription reducer.
                        This is not needed for aggregation done offline
  --strip-sw            Strip "sw-" for tag names (only used for shakespeares
                        world)
  -m METADATA, --metadata METADATA
                        Path to the panoptes subject data dump `csv` file.
                        When provided the `metadata` column will be included
                        in the output `csv` table


```

This script uses the following python packages:
```
json
pandas
progressbar
panoptes_aggregation
```
