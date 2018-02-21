# ASM consensus text files
This script takes the caesar reduction file for ASM and turns it into a series of text files with the consensus text (one file for each subject).

This is a command line script.  Show the help text with:

```
> python consensus_txt.py -h

Turn caesar extracts for ASM into consensus text files

positional arguments:
  input_file        The reduction export from caesar for the workflow
  output_folder     The folder to save the `.txt` files to

optional arguments:
  -h, --help        show this help message and exit
  -s, --show-score  Show consensus scores for each line of text
```

This script uses the following python packages:
```
pandas
progressbar
```
