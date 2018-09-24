# ASM consensus text files
This script takes the caesar reduction file for ASM and turns it into a series of text files with the consensus text (one file for each subject).

This is a command line script.  Show the help text with:

```
> python consensus_txt.py -h
usage: consensus_txt.py [-h] [-s] [-r] [-k REDUCER_KEY] [--strip-sw] [-c CSV]
                        [-m METADATA]
                        input_file output_folder

Turn caesar reductions from ASM into consensus text files

positional arguments:
  input_file            The reduction export from caesar for the workflow
  output_folder         The folder to save the `.txt` files to

optional arguments:
  -h, --help            show this help message and exit
  -s, --show-score      Show consensus scores for each line of text
  -r, --replace-arrow   Replace `=>` with `:` in csv dump before processing
                        (only needed for old Caesar data dumps)
  -k REDUCER_KEY, --reducer-key REDUCER_KEY
                        The reducer key to use, if left blank no key is used
                        (useful for data processed offline)
  --strip-sw            Strip "sw-" for tag names
  -c CSV, --csv CSV     Make a `.csv` file with this name contaning all the
                        transcriptions
  -m METADATA, --metadata METADATA
                        The `metadata` column of this subjects `csv` file will
                        be unpaced into the ouput `csv` table

```

This script uses the following python packages:
```
pandas
progressbar
```
