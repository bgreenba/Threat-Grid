#!/bin/python3
##BI2CSV
# Uses Threat Grid API to fetch Behaviour Indicatrors and converts into CSV
# Omits links field: too damn bad


import sys, configparser,argparse, fileinput, requests, json



    
def getopts(argv):
    parser = argparse.ArgumentParser(
        description='BI2CSV - download the current list of active Behaviour Indicators and output it as CSV')
    #program level options
    config=parser.add_argument_group('Configuration','Program and API configuration settings')
    config.add_argument('-c', '--cfg_file', help='specify a configuration file (default %(default)s)',
                        type=argparse.FileType('r'), default='BI2CSV.cfg')
    config.add_argument('-f', '--file', help='specify an input file (default is STDIN).', default=sys.stdin)
    config.add_argument('-k', '--api_key', help='specify an API key value (overrides config file)')
    config.add_argument('-s', '--server_name', help='specify a server hostname (overrides config file)')
    config.add_argument('-v', '--verbose', help='print diagnostic and troubleshooting information to stdout. Once for a reasonable amount, more for lots (0-3)',
                        action='count', default=0)

    #make with the args already
    args = parser.parse_args()
    return(args)


oporder=['title', 'name', 'description', 'trigger', 'category', 'tags',
         'created-at-date', 'last-modified-date',
         'additional-info', 'severity', 'confidence',
         'mitre-tactics']
compounds=['tags', 'category', 'mitre-tactics']

def verbose(msg, vlvl=1):
    if args['verbose'] >=vlvl: print(msg,'\n')

def myget(url,QS):
    tries=0
    errlog=[]
    while tries < 5:
        try:
            verbose('myget function trying received data: url="'+url+'"; QS="'+QS+'"',2)
            r = requests.get(url,params=QS)
            verbose('Request URL:'+ r.url+'\n',2)
            if r.status_code // 100 != 2:
                return "Error: {}".format(r)
            try:
                return r.json()
            except:
                return "Error: Non JSON response - {}".format(r.text)
        except requests.exceptions.RequestException as e:
            errlog.append('Error: Exception - {}'.format(e))
            tries=tries+1    
    return errlog

##get ready
# get cmdline options
args=vars(getopts(sys.argv))
verbose('\n'.join(['Command line options, including defaults','\n'.join('{}={}'.format(key, val) for key, val in args.items())]),2)

# Read config file to get settings
verbose('reading config file '+args['cfg_file'].name)
config = configparser.RawConfigParser()
config.read(args['cfg_file'].name)

#get all the main config
mainConfig=dict(config.items('PROGRAM'))

#get all the server config
serverConfig=dict(config.items('SERVER'))

#glom together
finalConfig=mainConfig.copy()
finalConfig.update(serverConfig)

#overwrite config file with cmdline args where applicable
for key,val in args.items():
    if val is not None:
        finalConfig[key]=val

verbose('\n'.join(['Final config, including defaults','\n'.join('{}={}'.format(key, val) for key, val in finalConfig.items())]),2)

#check for API key
if finalConfig['api_key'] is None or len(finalConfig['api_key']) != 26 :
    print('''No API key or invalid API key - this won't work. Exiting.''')
    exit()
api_key_QS='api_key='+finalConfig['api_key']

##do some preliminary construction
#make reusable root and search paths
finalConfig['root_path']='https://'+finalConfig['server_name']+finalConfig['api_path']+'/'
indicators_url=finalConfig['root_path']+finalConfig['indicators_path']



##do the thing(s)
verbose('downloading behaviour indicators')

BIjson=myget(indicators_url, api_key_QS)

#print out header row
print(*oporder, sep=',') 

for BI in BIjson['data']['indicators']:
    verbose('parsing: '+BI['name'], 2)
    verbose(BI,3)
    op=[]
    for field in compounds:
        verbose('de-listing '+field+' field into cdl',3)
        BI[field]=','.join(BI[field])
        verbose('     '+BI[field],3)
    for field in oporder:
        verbose(BI['name']+': '+field+': ',2)
        if BI[field] is None:
            BI[field]=""
        elif not isinstance(BI[field], str):
            BI[field]=str(BI[field])
        else: BI[field]=BI[field].replace('"',"'").replace('\n','')
        verbose('     '+BI[field],2)
        op.append('"'+BI[field]+'"')
    print(','.join(op))


exit()
