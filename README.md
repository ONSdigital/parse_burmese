# parse_burmese
Script to extract the Burmese from a translation csv and create translation yaml files for SDG translations

# Method

1) import all English/Burmese translations from [the translations csv](https://github.com/jwestw/parse_burmese/blob/main/translations_for_myanmar.csv)
2) as both languages are in one column, seperate them
3) recombine in a dataframe with 'en' and 'burm' columns and check for mismatches --> `en_burm_trans`
4) download (manually) the official [english-english translation yaml files](https://github.com/open-sdg/sdg-translations/tree/master/translations/en) 
5) turn yaml files into dataframe --> `all_translations`

`all_translations` has the structure: 

| yamlfilename    | key_word     | sentence     |
| :------------- | :----------: | -----------: |
|  indicator | clear_all   | Clear all    |


6) using the strings in the 'en' column  in `en_burm_trans` as search strings, find matches in 'sentence' column of `all_translations` and return the key_word and yamlfilename as a string, creating `yamlfilename` and `key_word` columns in `en_burm_trans`
7) Filter `en_burm_trans` by yaml_file, and write out to `.yaml` files. 
- Each `yamlfilename` should be its own yaml file. e.g. 'indicators.yml'
- within the yaml file the key_word should be matched with the Burmese, e.g. 'clear_all: အားလုံးကိုဖျက်ရန်'


# Outstanding challenges

- There are some non-unique sentences. Do not know how to handle multiple `key_word`, `yamlfilename` combinations. Currently just printing out the dataframe. 
- There are some sentences that for whatever reason are not being matched, even when searching for smaller sub-strings of the large sentence (currently chopping search term randomly into thirds, quarters etc). 
