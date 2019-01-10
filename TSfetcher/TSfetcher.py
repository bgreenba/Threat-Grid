#!/bin/python3
##TSfetcher
# Uses Threat Grid API to fetch Threat Scores for bulk file hashes


import sys, configparser,argparse, fileinput, requests, json



    
def getopts(argv):
    parser = argparse.ArgumentParser(
        description='TSfetcher - Bulk hash lookups against TG to get Threat Scores for files',
        epilog='''This script can be used to query Threat Grid for the Threat Scores of files based on checksum lookups.
            It will check for the scores of all submissions of files with each given filehash, and perform some rudimentary statistics (min, max, average, most recent).
            If no file is specified on the command line, it will read from STDIN. Either way, it expects input to be one hash per line, with no other content.
            If there is no match for a hash, there will be no row for that hash in the output.''' 
        )
    #program level options
    config=parser.add_argument_group('Configuration','Program and API configuration settings')
    config.add_argument('-c', '--cfg_file', help='specify a configuration file (default %(default)s)',
                        type=argparse.FileType('r'), default='TSfetcher.cfg')
    config.add_argument('-f', '--file', help='specify an input file (default is STDIN).', default=sys.stdin)
    config.add_argument('-k', '--api_key', help='specify an API key value (overrides config file)')
    config.add_argument('-s', '--server_name', help='specify a server hostname (overrides config file)')
    config.add_argument('-v', '--verbose', help='print diagnostic and troubleshooting information to stdout. Once for a reasonable amount, more for lots (0-3)',
                        action='count', default=0)

    #make with the args already
    args = parser.parse_args()
    return(args)


oporder=['hash','count','first_seen','last_seen','min_score','avg_score','max_score','last_score']

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

##do some preliminary construction
#make reusable root and search paths
finalConfig['root_path']='https://'+finalConfig['server_name']+finalConfig['api_path']
samples_url=finalConfig['root_path']+finalConfig['samples_path']

#test connection
url='https://'+finalConfig['server_name']+'/api/v3'+finalConfig['whoami_path']
api_key_QS='api_key='+finalConfig['api_key']
if myget(url, api_key_QS)['api_version'] != 3:
    print('API failure. Something went wrong. Check API key, then server settings?')

##do the thing(s)
verbose('starting lookups')
#print out header row
print(*oporder, sep=',') 

#iterate through input
for line in fileinput.input(args['file']):
    line=line.strip()
    thisout={}
    thisprint=[]
    verbose( 'starting query for hash '+line)
    thisout['hash']=line
    data=api_key_QS+'&checksum_sample='+line
    hash_search=myget(samples_url+finalConfig['search_path'],data)
    verbose(hash_search,3)
    thisout['count']=str(hash_search['data']['current_item_count'])
    if int(thisout['count'])>0:
        these_samples =[]
        dates=[]
        scores=[]
        maxdate='0'
        lastscore='0'
        #iterate through samples in response
        for sample in hash_search['data']['items']:
            verbose('getting threat report',2)
            threatreport=myget('/'.join([samples_url,sample['sample'],finalConfig['threat_path']]), api_key_QS)
            these_samples.append({'date':sample['ts'], 'score':threatreport['data']['score']})
            dates.append(sample['ts'])
            scores.append(threatreport['data']['score'])
        thisout['first_seen']=min(dates)
        thisout['last_seen']=max(dates)
        thisout['min_score']=str(min(scores))
        thisout['max_score']=str(max(scores))
        thisout['avg_score']=str(round(sum(scores)/int(thisout['count']),2))
        for item in these_samples:
            if item['date'] == thisout['last_seen']:
                thisout['last_score']=str(item['score'])
        
        #print out output
        for field in oporder:
            thisprint.append(thisout[field])
        print(','.join(thisprint))


#print ('hash,count,first_seen,last_seen,min_score,avg_score,max_score,last_score')
#for item in output:
#   print (','.join([item['hash'],str(item['count']),item['first_seen'],item['last_seen'],str(item['min_score']),str(item['avg_score']),str(item['max_score']),str(item['last_score'])]))
        
    
    




