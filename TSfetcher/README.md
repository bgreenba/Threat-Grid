Threat Score Fetcher
Takes a list of hashes from a file or STDIN and looks up each one's submission history in Threat Grid. 

This script can be used to query Threat Grid for the Threat Scores of files
based on checksum lookups. It will check for the scores of all submissions of
files with each given filehash, and perform some rudimentary statistics (min,
max, average, most recent). If no file is specified on the command line, it
will read from STDIN. Either way, it expects input to be one hash per line,
with no other content. If there is no match for a hash, there will be no row
for that hash in the output.


```
TSfetcher.py -h
usage: TSfetcher.py [-h] [-c CFG_FILE] [-f FILE] [-k API_KEY] [-s SERVER_NAME]
                    [-v]

TSfetcher - Bulk hash lookups against TG to get Threat Scores for files

optional arguments:
  -h, --help            show this help message and exit

Configuration:
  Program and API configuration settings

  -c CFG_FILE, --cfg_file CFG_FILE
                        specify a configuration file (default TSfetcher.cfg)
  -f FILE, --file FILE  specify an input file (default is STDIN).
  -k API_KEY, --api_key API_KEY
                        specify an API key value (overrides config file)
  -s SERVER_NAME, --server_name SERVER_NAME
                        specify a server hostname (overrides config file)
  -v, --verbose         print diagnostic and troubleshooting information to
                        stdout. Once for a reasonable amount, more for lots
                        (0-3)


```
