
# coding: utf-8
# Author: James Westwood

# imports
import pandas as pd
import os
import yaml
import random
import re

# importing the whole dataset, containing both English and Burmese translations
en_burm_trans_df = pd.DataFrame.from_csv("translations_for_myanmar.csv", header=None)

# Seperating the English out (every other line starting at 0)
en = en_burm_trans_df.iloc[0::2]

# Seperating the Burmese out (every other line starting at 1)
burm = en_burm_trans_df.iloc[1::2]

# Combining the English and Burmese Dataframes (they are not Series) into a new dataframe, 
# via turning them into a  list (nuts, I know, but it's what worked) 
en_burm_trans_df = pd.DataFrame({'en':list(en.index),'burm':list(burm.index)})

# *** DATA CLEANING ***
def trans_data_cleaner(df=en_burm_trans_df):  # The imported csv sometimes has '***' or '[Translation needed]' in the burm column when a Translation is    # missing so fixing that   df.burm.replace({'***':'',                   '[Translation needed]':'',                   u'U+2424':'',                   u'U+000A':' '},                   value=None, inplace=True, regex=False)  # Check the replacement has occured   if df.burm.str.contains('***', regex=False).any():       print("WARNING: replacement of '***' has not been successful")   if df.burm.str.contains('[Translation needed]', regex=False).any():       print("WARNING: replacement of '[Translation needed]' has not been successful")  # The imported csv sometimes has randomly placed newline characters ('\n') in the Burmese text    #  which need to be removed. regex should be True here   df.burm.replace(to_replace=r'\\n', value=' ', inplace=True, regex=True)   # Also replacing quote marks in the Burmese   df.burm.replace(to_replace=r'\'', value='', inplace=True, regex=True)   return df   
# clean the data 
en_burm_trans_df = trans_data_cleaner(df=en_burm_trans_df)

# Checking it's worked. This will check if what's contained in the 'en' dataset are all A-Z western alphabet 
# characters. If True, they are all A-Z,a-z.
pattern = re.compile("[A-Za-z]+")
if en.reset_index().loc[:,0].str.contains(pattern).all():   print("All characters in the English column of en_burm_trans_df seems to be Western alphabet")
else:   print("""Warning: non-Western alphabet characters found in the English column of en_burm_trans_df.       Check English column and check logic of this QA check.""")



# exporting the translations to csv. This is suppressed at the moment because I do not want to overwrite the manual work I have done. 
export_csv = False
if export_csv:   en_burm_trans_df.to_csv("en_burms_trans.csv", encoding="utf8")

# define function to grab all the English sentences from the official translations
def get_official_en_trans_df():   """   Grabs all of the official English from the downloaded "en" translations yaml files    which will provide:   1) the English text    2) the corresponding key.       The keys can be used to build the Burmese yaml later.       returns:       dict of all data from yaml files   """   source_yaml_dir = "official_translations\\en"   all_yamls_dict = {}   for file in os.listdir(source_yaml_dir):       file_name = file[:-4]       f = open(os.path.join(source_yaml_dir, file), 'r',  encoding="utf8")       all_yamls_dict[file_name] = {}       for key,value in yaml.load(f).items():           all_yamls_dict[file_name][key] = value   return all_yamls_dict

#grab all english yml files into a dict
all_yamls_dict = get_official_en_trans_df()

# Now we have all the translations from the yamls, we can make them into a dataframe
# This dataframe is needed for searching the values (translations) and picking the correct key
# Require structure is 
# --------------------------------------
# ¦ yamlfilename ¦ key_word ¦ sentence ¦
# ¦ -----------------------------------
official_en_trans_df = (pd.DataFrame(data=[(file_name, key_word, sentence)                                      for file_name in all_yamls_dict.keys()                                      for key_word,sentence in all_yamls_dict[file_name].items()],                                columns=['yaml_filename', 'key_word', 'en']))
# Nice!

# Questions to answer for Quality Assurance:
# 1) Is the number of English sentences grabbed from the csv "translations_for_myanmar.csv" then into en_burm_trans_df
#   the same as what has been grabbed from all the official en translations in official_en_trans_df?
# 2) Before matching English sentences, are there repeats? Repeats might cause a single (first found) match when there needs
#   multiple matches.
# 3) After the matches (via merge) are made on the English sentences, are the number of Burmese sentences the same in 
#   the the original en_burm_trans_df as there are in the resulting dataframe? If not, have some been lost and why?


# Answering QA #1
# Number of English sentences in en_burm_trans_df
en_trans_count = en_burm_trans_df.en.count()

# Number of English sentences in official translations
official_en_count = official_en_trans_df.en.count()

if en_trans_count != official_en_count:   if  official_en_count > en_trans_count:       print("""WARNING: There are more English sentences in official translations than in the English Burmese Translations           This means there will be some official translations that will not be matched with Burmese""")   else:       print("""WARNING: There are more English sentences in the En-Burmese Translations than in the official translations           This means there will be some Burmese translations that will not be matched with keywords and yaml filenames""")

# Answering QA #2
if en_burm_trans_df.en.duplicated().any():   print("WARNING: Some of the English sentences in the En-Burmese translations are duplicated.")   en_burm_rpts = True
if official_en_trans_df.en.duplicated().any():   print("WARNING: Some of the English sentences in the official En-En translations are duplicated.")

# If there are repeats are they occuring in the same places - e.g as an English sentence is repeated, is the Burmese
# repeated on the same row?
if en_burm_rpts:   if en_burm_trans_df.en.duplicated().equals(en_burm_trans_df.burm.duplicated()):       print("English and Burmese duplicates are happening on the same rows")

# define functions to output the dict to yaml and df to yaml
def write_dict_to_yaml(filename, dic_output):   """   Writes dictionary data to a yaml file in utf-8 encoding      Parameters:       filename (str): the name of the file to be written       dic_output (dict) the dictionary data to be written in the yaml file  Returns:       Bool: True if written (will throw error if it fails to write)   """   with open(f'{filename}.yml', 'w', encoding="utf-8") as outfile:       print(f'Writing {filename}.yml')       yaml.dump(dic_output, outfile, allow_unicode=True, default_flow_style=False) #encoding='utf-8'       return True       
# Merging the official_en_trans_df and the en_burm_trans_df
match_on_en_df = (official_en_trans_df.merge(                   right=en_burm_trans_df,                   on="en",                   how="inner")                   .reset_index(drop=True)                   ) #.drop_duplicates()

# Following the merge, find out which did not match well
# Grabbing those rows with empty cells in the columns of interest
empty_burms = match_on_en_df[pd.isnull(match_on_en_df.burm)]
missing_burms_count = match_on_en_df.burm[match_on_en_df.burm.isnull()].shape[0]
empty_yamls = match_on_en_df[pd.isnull(match_on_en_df.yaml_filename)]
missing_yamls_count = match_on_en_df.yaml_filename[match_on_en_df.yaml_filename.isnull()].shape[0] 
empty_key_words = match_on_en_df[pd.isnull(match_on_en_df.key_word)]
missing_key_words_count = match_on_en_df.key_word[match_on_en_df.key_word.isnull()].shape[0] 

# Additional QA
if missing_burms_count > 0:   print(f"WARNING: There are {missing_burms_count} missing Burmese sentences that need to be translated")
if missing_yamls_count > 0:   print(f"WARNING: There are {missing_yamls_count} missing yaml file names")
if missing_key_words_count > 0:   print(f"WARNING: There are {missing_key_words_count} missing key words")

# Writing each of the dataframes containing empty cells to their own csvs
export_csv = False
if export_csv:   empty_burms.to_csv("empty_burms.csv", encoding="utf-8-sig", index=False)   empty_yamls.to_csv("empty_yamls.csv", encoding="utf-8-sig", index=False)   empty_key_words.to_csv("empty_key_words.csv", encoding="utf-8-sig", index=False)

# keeping this out of the `if export_csv` because I want to inspect the results
match_on_en_df.to_csv("match_on_en_df.csv", encoding="utf-8-sig", index=False)

# *** OUTPUTTING TRANSLATIONS TO YAML FILES ***

def put_dfs_in_dict(df):   """ Split the merged dataframe into smaller dataframes, one for each yaml file.       Place each df into a dictionary using the yaml_file name as a key.       Also drops the 'en' column in the df because the English is not needed as output.       And drops the yaml_filename col because it's not needed in the output; instead       the yaml_filename will be used to name the file when written."""   res = {} # empty results dictionary   for yaml_file_name in df.yaml_filename.unique():       df_filtered = df[df['yaml_filename'] == yaml_file_name]       df_clean = df_filtered.drop(['en','yaml_filename'], axis=1)       # use file_name as a key       res[yaml_file_name] = df_clean   return res

res = put_dfs_in_dict(df=match_on_en_df)

# # Try to write each df to a dictionary, then to yamls
#the yaml_filename is used to name the file when written
for yaml_file_name in res.keys():   # get df and set the index to key_word    df = res[yaml_file_name].set_index("key_word")   dic = df.to_dict()['burm']   file_name = str(yaml_file_name)   write_dict_to_yaml(file_name, dic_output=dic)
