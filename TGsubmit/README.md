This script checks with Cisco Threat Response to see if the file is known to any AMP or Threat Grid modules the user has configured. 
If the file is unknown, it then checks to see if the file has been submitted to threat Grid in the last 30 days. 
If neither of the above are true, it will submit the file the Threat Grid for analysis. 

This was largely pasted together Frankenstyle from scripts available in the Cisco Security Github.


```
TGsubmit.py -h
usage: TGsubmit.py [-h] [-c CFG_FILE] [-v] [-x]
                   [--threat_grid_server THREAT_GRID_SERVER]
                   [--threat_grid_api_key THREAT_GRID_API_KEY] [-p]
                   [--threat_response_server THREAT_RESPONSE_SERVER]
                   [--threat_response_api_clientID THREAT_RESPONSE_API_CLIENTID]
                   [--threat_response_api_client_pass THREAT_RESPONSE_API_CLIENT_PASS]
                   [-t THREAT_RESPONSE_TOKEN_FILE]
                   filename [filename ...]

TGsubmit - take specifed files and submit to Threat Grid if currently unknown
to TG and AMP FileDB

optional arguments:
  -h, --help            show this help message and exit

Configuration:
  Program and API configuration settings

  -c CFG_FILE, --cfg_file CFG_FILE
                        specify a configuration file (default TGsubmit.cfg)
  -v, --verbose         print diagnostic and troubleshooting information to
                        stdout. Once for a reasonable amount, more for lots
                        (0-3)
  -x, --experiment      do everything except submit the file(s)
  filename              name of the file(s) to be looked up and potentially
                        submitted

Threat Grid Options:
  Threat Grid API configuration settings

  --threat_grid_server THREAT_GRID_SERVER
                        specify a server hostname (overrides config file)
  --threat_grid_api_key THREAT_GRID_API_KEY
                        specify an API key for Threat Grid (overrides config
                        file)
  -p, --private         submit the file privately

Threat Response Options:
  Threat Response API configuration settings

  --threat_response_server THREAT_RESPONSE_SERVER
                        specify a server hostname (overrides config file)
  --threat_response_api_clientID THREAT_RESPONSE_API_CLIENTID
                        specify an API clientID for Threat Response (overrides
                        config file)
  --threat_response_api_client_pass THREAT_RESPONSE_API_CLIENT_PASS
                        specify an API client password for Threat Response
                        (overrides config file)
  -t THREAT_RESPONSE_TOKEN_FILE, --threat_response_token_file THREAT_RESPONSE_TOKEN_FILE
                        The name of the file in which to store/read the Threat
                        Response access token

```
