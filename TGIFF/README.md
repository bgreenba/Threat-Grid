Threat Grid Intelligence Feed Fetcher

(Perhaps named on a Friday)

This script can be used to retrieve threat intel feeds from the Cisco Threat
Grid API. It reads configuration paramaters from the command line, and reads
defaults from a configuration file. Usage of this script requires a valid API
key. This utility is provided as an example, with no guarantees or support
options.

```
TGIFF.py -h
usage: TGIFF.py [-h] [-a AFTER_TIME] [-b BEFORE_TIME] [-c CFG_FILE]
                [-d FEED_DATE] [-f OUTPUT_FORMAT] [-x] [-k API_KEY]
                [-l LOG_FILE] [-m] [-o OUT_FILE] [-p PARAMETERS]
                [-s SERVER_NAME] [--rtfm] [-v]
                [feedName]

TGIFF: Threat Grid Intelligence Feeds Fetcher

positional arguments:
  feedName              specify the desired feed

optional arguments:
  -h, --help            show this help message and exit
  -a AFTER_TIME, --after_time AFTER_TIME
                        Specify a start time for the feed window. You want the
                        data from after this time. Must be in format
                        "%Y-%m-%dT%H:%M:%SZ". (default one hour ago, or one
                        hour before before_time if specified) Only valid for
                        non-curated/v2 feeds
  -b BEFORE_TIME, --before_time BEFORE_TIME
                        Specify an end time for the feed window. You want the
                        data from before this time. Must be in format
                        "%Y-%m-%dT%H:%M:%SZ". (default now, or one hour after
                        after_time if specified) Only valid for non-curated/v2
                        feeds
  -c CFG_FILE, --cfg_file CFG_FILE
                        specify a configuration file (default TGIFF.cfg))
  -d FEED_DATE, --feed_date FEED_DATE
                        specify a date - for curated/v3 feeds ONLY
  -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                        specify a format - for curated/v3 feeds ONLY
  -x, --experiment      Do everything except request the feed. Most useful
                        with -v
  -k API_KEY, --api_key API_KEY
                        specify an API key value (overrides config file)
  -l LOG_FILE, --log_file LOG_FILE
                        specify a log file (overrides config file)
  -m, --feed_menu       print out the menu of available feeds in the config
                        file (not from the API) and exit
  -o OUT_FILE, --out_file OUT_FILE
                        specify an output file (default STDOUT)
  -p PARAMETERS, --parameters PARAMETERS
                        specify additional parameters as a single string TODO
  -s SERVER_NAME, --server_name SERVER_NAME
                        specify a server hostname (overrides config file)
  --rtfm                print a link to the API documentation for the
                        specified feed and exit (Threat Grid account required)
                        If no feed is specified it will print out links for
                        all feed types
  -v, --verbose         print diagnostic and troubleshooting information to
                        stdout

```
