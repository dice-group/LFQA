# Script to read the HTML table from BENG results
# Open the new output file (w) and old tsv file (r)
    # Generate header
    # Write the header line
    # For each line in the old tsv
        # split using tab
        # extract the experiment uri
        # use uri to extract the html table
        # gather the values into a list
        # extend the split list with values list
        # write the full list to the output file
# Imports
import pandas as pd
# vars
output_file = 'evaluation_results.tsv'
old_tsv = 'experiment_details.tsv'
header_arr = ['Test Name', 'Language', 'Components', 'Gold File', 'Prediction File', 'Uploaded Gold File', 'Uploaded Prediction File', 'Experiment URI']

# Open the new output file (w) and old tsv file (r)
with open(output_file,'w') as fout, open(old_tsv,'r') as fin:
    old_arr = [x.strip().split('\t') for x in fin.readlines()]
    # Generate header
    sample_uri = old_arr[0][7]
    sample_df = pd.read_html(sample_uri)
    res_header_arr = [x for x in sample_df[0]]
    header_arr.extend(res_header_arr)
    # print(header_arr)
    # Write the header line
    fout.write('\t'.join(header_arr) + '\n')
    # For each line in the old tsv
    for line_arr in old_arr:
        # extract the experiment uri
        uri = line_arr[7]
        # use uri to extract the html table
        df = pd.read_html(uri)
        # gather the values into a list
        val_arr = [str(df[0][item].to_dict()[0]) for item in df[0]]
        # extend the split list with values list
        line_arr.extend(val_arr)
        # write the full list to the output file
        fout.write('\t'.join(line_arr) + '\n')
print('Done')