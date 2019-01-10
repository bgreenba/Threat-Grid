#!/usr/bin/python3
import requests, datetime, configparser, argparse, sys, json, hashlib, os

TR_SESSION = requests.session()
TG_SESSION = requests.session()

def get_cmd(argv):
    parser = argparse.ArgumentParser(
        description='TGsubmit - take specifed files and submit to Threat Grid if currently unknown to TG and AMP FileDB',
        epilog='''Poorly coded in spare time by pasting together the work of better programmers - provided without warranties or support''' 
        )
    #program level options
    config=parser.add_argument_group('Configuration','Program and API configuration settings')
    config.add_argument('-c', '--cfg_file', help='specify a configuration file (default %(default)s)',
                        type=argparse.FileType('r'), default=os.path.basename(sys.argv[0]).replace('.py','')+'.cfg')
    
    config.add_argument('-v', '--verbose', help='print diagnostic and troubleshooting information to stdout. Once for a reasonable amount, more for lots (0-3)',
                        action='count', default=0)
    config.add_argument('-x', '--experiment', help='do everything except submit the file(s)',action='store_true')
    config.add_argument('filename', nargs='+',
                    help='name of the file(s) to be looked up and potentially submitted')

    #threat grid options
    TGopts=parser.add_argument_group('Threat Grid Options','Threat Grid API configuration settings')
    TGopts.add_argument('--threat_grid_server', help='specify a server hostname (overrides config file)')
    TGopts.add_argument('--threat_grid_api_key', help='specify an API key for Threat Grid (overrides config file)')
    TGopts.add_argument('-p', '--private', help='submit the file privately', action='store_true', default=False)

    #threat response options
    TRopts=parser.add_argument_group('Threat Response Options','Threat Response API configuration settings')
    TRopts.add_argument('--threat_response_server', help='specify a server hostname (overrides config file)')
    TRopts.add_argument('--threat_response_api_clientID', help='specify an API clientID for Threat Response (overrides config file)')
    TRopts.add_argument('--threat_response_api_client_pass', help='specify an API client password for Threat Response (overrides config file)')
    TRopts.add_argument('-t', '--threat_response_token_file', help="The name of the file in which to store/read the Threat Response access token")

    #make with the args already
    cmd = parser.parse_args()
    return(cmd)

   
def get_config_file_opts():
    # Read config file to get settings
    verbose('reading config file '+cmd['cfg_file'].name, 2)
    config = configparser.RawConfigParser()
    config.read(cmd['cfg_file'].name)

    #get all the general config
    GENcfg=dict(config.items('General'))
    verbose('\n'.join(['General options from config file are:','\n'.join('{}={}'.format(key,val) for key, val in GENcfg.items())]),3)
    #get all the TG config
    global TGcfg
    TGcfg=dict(config.items('ThreatGrid'))
    verbose('\n'.join(['Threat Grid options from config file are:','\n'.join('{}={}'.format(key,val) for key, val in TGcfg.items())]),3)
    #get all the TR config
    global TRcfg
    TRcfg=dict(config.items('ThreatResponse'))
    verbose('\n'.join(['Threat Response options from config file are:','\n'.join('{}={}'.format(key,val) for key, val in TRcfg.items())]),3)

    #glom together
    fileConfig=GENcfg.copy()
    fileConfig.update(TGcfg)
    fileConfig.update(TRcfg)

    return(fileConfig)
    
def get_all_opts():
    # get cmdline options
    global cmd
    cmd=vars(get_cmd(sys.argv))
    verbose('\n'.join(['Command line options, including defaults','\n'.join('{}={}'.format(key, val) for key, val in cmd.items())]),2)

    #get cfg file options
    finalConfig=get_config_file_opts()

    #overwrite config file items with cmd line items
    for key,val in cmd.items():
        if val is not None:
            finalConfig[key]=val
     

    #make some userful vars now
    finalConfig['TGroot']='https://'+finalConfig['threat_grid_server']+'/'+finalConfig['threat_grid_api_root']+'v'+finalConfig['threat_grid_api_ver']+'/'
    finalConfig['TRroot']='https://'+finalConfig['threat_response_server']+'/'+finalConfig['threat_response_api_root']

    verbose('final options are:\n'+'\n'.join('{}={}'.format(key,val) for key, val in finalConfig.items()),2)
    return(finalConfig)


def verbose(msg, vlvl=1):
    if cmd['verbose'] >=vlvl: print(msg,'\n')

def TR_generate_token():
    ''' Generate a new access token and write it to disk'''
    token_url=globalConfig['TRroot']+globalConfig['threat_response_token_path']
    headers = {'Content-Type':'application/x-www-form-urlencoded', 'Accept':'application/json'}
    payload = {'grant_type':'client_credentials'}

    verbose('getting auth token from '+token_url+' with client_id '+globalConfig['threat_response_client_id'], 3)
    response = requests.post(token_url, headers=headers,
                         auth=(globalConfig['threat_response_client_id'],
                               globalConfig['threat_response_client_pass']),
                         data=payload)

    if TR_unauthorized(response):
        sys.exit('Unable to generate new token!\nCheck your CLIENT_ID and CLIENT_PASSWORD')

    response_json = response.json()
    access_token = response_json['access_token']

    with open(globalConfig['threat_response_token_file'], 'w') as token_file:
        token_file.write(access_token)

def TR_get_token():
    ''' Get the access token from disk if it's not there generate a new one
    '''
    for i in range(2):
        while True:
            try:
                with open(globalConfig['threat_response_token_file'], 'r') as token_file:
                    access_token = token_file.read()
                    return access_token
            except FileNotFoundError:
                verbose('threat response token file ('+globalConfig['threat_response_token_file']+') not found, generating new token.')
                TR_generate_token()
            break    

def TR_unauthorized(response):
    ''' Check the status code of the response
    '''
    if response.status_code == 401:
        return True
    return False

def TR_check_auth(function, param):
    ''' Query the API and validate authentication was successful
        If authentication fails, generate a new token and try again
    '''
    response = function(param)
    if TR_unauthorized(response):
        print('Auth failed, generating new token.')
        TR_generate_token()
        return function(param)
    return response

def TR_query(observable):
    ''' Pass the functions and parameters to check_auth to query the API
        Return the final response
    '''
    response = TR_check_auth(TR_inspect, observable)
    inspect_output = response.text
    response = TR_check_auth(TR_enrich, inspect_output)
    return response

def TR_inspect(observable):
    '''Inspect the provided observable and determine its type
    '''
    inspect_url = globalConfig['TRroot']+globalConfig['threat_response_inspect_path']

    access_token = TR_get_token()

    headers = {'Authorization':'Bearer {}'.format(access_token),
               'Content-Type':'application/json',
               'Accept':'application/json'}

    inspect_payload = {'content':observable}
    inspect_payload = json.dumps(inspect_payload)

    response = TR_SESSION.post(inspect_url, headers=headers, data=inspect_payload)
    return response

def TR_enrich(observable):
    ''' Query the API for a observable
    '''

    enrich_url = globalConfig['TRroot']+globalConfig['threat_response_enrich_path']

    access_token = TR_get_token()

    headers = {'Authorization':'Bearer {}'.format(access_token),
               'Content-Type':'application/json',
               'Accept':'application/json'}

    response = TR_SESSION.post(enrich_url, headers=headers, data=observable)

    return response



def get_hash(filename):
    verbose('getting hash value for file '+filename, 2)
    hashit=hashlib.sha256()
    with open(filename, 'rb') as thisfile:
        buf = thisfile.read(65536)
        while len(buf)>0:
            hashit.update(buf)
            buf=thisfile.read(65536)
    verbose('hash value: '+hashit.hexdigest())
    return(hashit.hexdigest())

def TR_isknown(this_hash):
    known=False
    dtnow=datetime.datetime.now()
    response = TR_query(this_hash)
    response_json = response.json()
    verbose('response JSON:\n'+response.text,2)

        
    for module in response_json['data']:
        module_label=module['module']+' ('+module['module-type']+'): '
        verbose(module_label,2)
        if module['module-type'] in ['POKEDeliberateModule','ThreatgridModule']:
            if 'verdicts' in module['data'] and module['data']['verdicts']['count'] > 0:
                for doc in module['data']['verdicts']['docs']:
                   verbose('doctype: {}, valid from {} to {}'.format(doc['type'],doc['valid_time']['start_time'],doc['valid_time']['end_time']),2)
                   if doc['type']=='verdict':
                       if doc['disposition_name'] not in ['Unknown', 'unknown']:
                           if datetime.datetime.strptime(doc['valid_time']['end_time'],"%Y-%m-%dT%H:%M:%S.%fZ") > dtnow:
                               disposition = doc.get('disposition', 'None')
                               disposition_name = doc.get('disposition_name', 'None')
                               known=True
                               verbose(module_label+disposition_name+' '+doc['valid_time']['end_time'])
                               verbose('file is known!')
                               return(known)
                           else: verbose (module_label+'{} ({}): verdict not currently valid (current time {})'.format(dtnow),2)
                       else: verbose(module_label+'verdict = unknown')
                   else: verbose(module_label+'doc is not a verdict')
            else: verbose(module_label+'no verdicts from this module')
        else: verbose(module_label+'not AMP or TG')
    verbose('file is known? {}'.format(known))
    return(known)

def TG_isRecent(this_hash):
    verbose('searching for TG submissions of hash '+this_hash+' within the last {} days'.format(globalConfig['threat_grid_max_days']),2)

    #prep URLs and time
    hash_url=globalConfig['TGroot']+globalConfig['threat_grid_samples_search_path']
    hash_data='&'.join(['api_key='+globalConfig['threat_grid_api_key'],'checksum_sample='+this_hash])
    samples_url=globalConfig['TGroot']+globalConfig['threat_grid_samples_path']
    samples_data='api_key='+globalConfig['threat_grid_api_key']
    these_samples=[]
    sample_date=[]
    dtnow=datetime.datetime.now()
    recently=False
    #search for the hash
    verbose('searching at '+hash_url+'?'+hash_data,2)
    hash_search=requests.get(hash_url, hash_data)
    hash_json=hash_search.json()
    verbose('hash search results json:\n'+str(hash_json),3)
    for sample in hash_json['data']['items']:
        verbose(sample['ts'], 3)
        delta=dtnow-datetime.datetime.strptime(sample['ts'],"%Y-%m-%dT%H:%M:%SZ")
        if delta.days < int(globalConfig['threat_grid_max_days']):
            verbose('hash was seen recently',2)
            recently=True
            return(recently)
    return(recently)


    
def TG_submit(filename):
    submit_url=globalConfig['TGroot']+globalConfig['threat_grid_submit_path']
    parameters = {'api_key': globalConfig['threat_grid_api_key'], 'private': globalConfig['private']}
    if not globalConfig['experiment']:
        with open(filename, 'rb') as sample:
            verbose('submitting file to '+submit_url,3)
            r = requests.post(submit_url, files={'sample': sample}, params=parameters)
            verbose(r.json(),3)
    else:  verbose('not submitting file because -x/--experiment was specified')
    return()
    
                                       
def main():
    global globalConfig
    globalConfig=get_all_opts()
    verbose('global options received are:\n'+'\n'.join('{}={}'.format(key,val) for key, val in globalConfig.items()),3)
    for this_file in globalConfig['filename']:
        verbose('file: '+this_file)
        this_hash=get_hash(this_file)
        if not TR_isknown(this_hash):
            if not TG_isRecent(this_hash):
                verbose('submitting file '+this_file)
                TG_submit(this_file)
            else: verbose('hash was submitted to TG in the last {} days, not submitting'.format(globalConfig['threat_grid_max_days']))
        else: verbose('file is known, not submitting')

if __name__ == '__main__':
    main()

    
