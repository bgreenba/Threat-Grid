##ANTI-TEDIUM
# Automated iNtuitive Threatgrid Interactions - Total Educational Deployment In Under a Minute
# bulk manage classroom or demo accounts for training purposes


import logging, requests, sys, configparser, argparse, json, re


    
def getopts(argv):
    parser = argparse.ArgumentParser(
        description='ANTI-TEDIUM: Automated iNtuitive Threatgrid Interactions - Total Educational Deployment In Under a Minute',
        epilog='''This script can be used by Organization Administrators to automate the creation and management of student accounts in a dedicated classroom TG Organization. USE WITH CARE -
                It will take the requested action in whatever organization is associated with the provided Admin API key.''' 
        )
    #program level options
    config=parser.add_argument_group('Configuration','Program and API configuration settings')
    config.add_argument('-c', '--cfg_file', help='specify a configuration file (default %(default)s)',
                        type=argparse.FileType('r'), default='anti-tedium.cfg')
    config.add_argument('-l', '--log_file', help='specify a log file (overrides config file)')
    config.add_argument('-k', '--api_key', help='specify an API key value (overrides config file)')
    config.add_argument('-s', '--server_name', help='specify a server hostname (overrides config file)')
    config.add_argument('-v', '--verbose', help='print diagnostic and troubleshooting information to stdout. Once for a reasonable amount, more for lots (0-3)',
                        action='count', default=0)
    config.add_argument('-x', '--experiment', help='Do everything except request the changes. Most useful with -v',
                        action='store_true')
    config.add_argument('--pave', help='modifies all action commands to ignore student counts and ranges, instead performing the actions on all non-admin account. USE WITH CARE.',
                        action = 'store_true')
    
    #class level options
    useropts=parser.add_argument_group('User Options','Student account options')
    useropts.add_argument('-n', '--num_students', help='specify number of student accounts to create (overrides config file) IGNORED if last_user spec\'d in cfg file or on cmd line')   
    useropts.add_argument('-u', '--username_prefix', help='prefix for user names [prefix01, prefix02,... prefix(n)](overrides config file)')
    useropts.add_argument('--instructor_email', help='''set instructor email address. (overrides config file). All student emails will be
                        constructed out of this information as follows: for an instructor address of instructor@domain,
                        all student emails will be set to instructor+prefix(n)@domain''')
    useropts.add_argument('--first_student', help='the suffix number for the first user (overrides config file)')
    useropts.add_argument('--last_student', help='the suffix number for the last user (overrides config file) OVERRIDES num_students')
    useropts.add_argument('--pad_length', help='the minimum number of digits for the numeric part of the username. (eg if pad_length=2, then foo_1 becomes foo_01). \
                        If unspecified, default to the length of the highest number in the range. If 0, then do not pad')
    
    #account action options
    acct_actions=parser.add_argument_group('Account Actions','Actions to take on non-admin accounts')
    acct_actions.add_argument('--make_users',
                        help='''This will create users as specified in the config file and cmdline parameters. This will be done prior to activate, deactive, or reset actions.''',
                        action='store_true')
    acct_actions.add_argument('--delete_users',
                        help='''This will delete users as specified in the config file and cmdline parameters. This will be done prior to activate, deactive, or reset actions.''',
                        action='store_true')
    acct_actions.add_argument('--nuke_from_orbit', help='''Delete all student accounts. ALL of them, regardless of prefix or supplied user count. When the nuke has passed, only admins shall remain.''',
                        action='store_true')
    acct_actions.add_argument('-a', '--activate',
                        help='''This will activate all specified non-admin users in the org''',
                        action='store_true')
    acct_actions.add_argument('-d', '--deactivate',
                        help='''This will de-activate all specified non-admin users in the org''',
                        action='store_true')
    acct_actions.add_argument('-r', '--reset_apikey',
                        help='''This will reset the API key for all specified non-admin users in the org''',
                        action='store_true')
    acct_actions.add_argument('--sample_limit',
                        help='''This will set the sample limit per day for all specified non-admin users. Follow it with a number.''',
                        default=False)
    acct_actions.add_argument('-p', '--password', help='sets password for all specified non-admin accounts in the org.',
                        default=False)
    
    #optional actions that don't change any org settings
    misc_options=parser.add_argument_group('Misc Actions','''Actions that don't affect user accounts but do have an output''')
    misc_options.add_argument('--print_roster', help='print out a list of all non-admin accounts and their corresponding API keys',
                        action='store_true')
    misc_options.add_argument('--print_deep_roster', help='print out a much more detailed list of all non-admin accounts',
                        action='store_true')
    misc_options.add_argument('--rtfm', help='''print a link to the API documentation for user management and exit.
                                        (Threat Grid account required)''',
                        action='store_true')


        
    #bulk shortcuts
    bulkactions=parser.add_argument_group('Setup and Shutdown batch actions','Shortcuts that set multiple actions')
    bulkactions.add_argument('-1','--setup', help='''sets up classroom - sets all nonadmin accounts to active, resets password and API keys, and prints roster
        (shortcut for -ra --print_roster)''',
                             action='store_true')
    bulkactions.add_argument('-0','--shutdown', help='shuts down classroom - sets all non-admin accounts to inactive and resets their API keys (shortcut for -rd)',
                             action='store_true')

    #make with the args already
    args = parser.parse_args()
    return(args)



def verbose(msg, vlvl=1):
    if args['verbose'] >=vlvl: print(msg,'\n')

def myget(url,QS):
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
        return 'Error: Exception - {}'.format(e)

def myput(url,data):
    try:
        verbose('myput function trying received data: url="'+url+'"; data="'+data+'"',2)
        r = requests.put(url,data=data)
        verbose('Request URL:'+ r.url+'\n',2)
        if r.status_code // 100 != 2:
            return "Error: {}".format(r.text)
        return(str(r.status_code)+'\n'+r.text)
    except requests.exceptions.RequestException as e:
        return 'Error: Exception - {}'.format(e)

def mydelete(url,data):
    try:
        verbose('mydelete function trying received data: url="'+url+'"; data="'+data+'"',2)
        r = requests.delete(url,data=data)
        verbose('Request URL:'+ r.url+'\n',2)
        if r.status_code // 100 != 2:
            return "Error: {}".format(r)
        return(str(r.status_code)+'\n'+r.text)
    except requests.exceptions.RequestException as e:
        return 'Error: Exception - {}'.format(e)
    
    
def mypost(url, data):
    verbose('mypost function trying received data: url="'+url+'"; data="'+data+'"',2)
    try:
        r = requests.post(url, data=data)
        verbose('Request URL:'+ r.url+'\n',2)
        if r.status_code // 100 != 2:
            return "Error: {}".format(r)
            verbose(r)
        return(str(r.status_code)+'\n'+r.text)

    except requests.exceptions.RequestException as e:
        return 'Error: Exception - {}'.format(e)

def getOrgID():
    verbose('getting your organization ID')
    data=(myget(finalConfig['root_path']+finalConfig['whoami_path'],'api_key='+finalConfig['api_key']))
    verbose(data)
    return(data['data']['organization_id'])

#get student list (all non-admin accts in org)
def getRoster():
    verbose('getting student roster')
    roster=list()
    url=finalConfig['root_path']+finalConfig['org_path']+'/'+orgID+finalConfig['roster_ep']
    reply=myget(url,'api_key='+finalConfig['api_key'])
    allUsers=reply['data']['users']
    for user in allUsers:
        if user['role'] == 'user':
            verbose('user login: '+user['login']+' role: '+user['role']+'... user is a student',3)
            roster.append(user)
        else: verbose('user login: '+user['login']+' role: '+user['role']+'... user is not a student',3)
    return(sorted(roster, key=lambda k: k['login']))

#get the first and last student numbers to be affected
def getStudentRange():
    verbose("getting student range",2)
    if not finalConfig['first_student']:finalConfig['first_student']='1'
    if not finalConfig['last_student']:
        if finalConfig['num_students']:
            finalConfig['last_student']=str(int(finalConfig['first_student'])+int(finalConfig['num_students']-1))
        else:
            print('''Either num_students or last_student must be specified for this operation - neither was found.''')
            exit()
    else: #last_student was spec'd, so we can ignore/overwrite any num_students that might have been here
            finalConfig['num_students']=str(int(finalConfig['last_student'])-int(finalConfig['first_student'])+1)

##get filtered student list (all non-admin accts in org that match the username pattern and are in the numbered range)
def getFilteredRoster():
    getStudentRange()
    verbose("getting filtered student roster",3)
    fullRoster=getRoster()
    filteredRoster=[]
    #if the user spec'd 'pave' then ignore all filters, actually
    if finalConfig['pave']:
        sure=input('You have specified the \'pave\' option. Are you sure you want to do this to all non-admin users? \'Y\' or \'y\' to proceed, any other to abort:')
        if sure in ['Y','y']:
            verbose('pave option was specified and user provided confirmation, returning unfiltered list',2)
            return(fullRoster)
    verbose("unfiltered roster length is {} rows".format(len(fullRoster)),3)
    verbose("filtering... user prefix is {} and range is {} to {}".format(finalConfig['username_prefix'],finalConfig['first_student'],finalConfig['last_student']),2) 
    for student in fullRoster:
        verbose(student['login'],3)
        #copy to filtered list if it does match spec'd prefix, and fall within suffix num range
        #if this returns anything, then it fit the pattern
        match=re.match(finalConfig['username_prefix']+"(\d*)$",student['login'])
        if match:
            num=match.group(1)
            #if num is between the range limits, then it is in range 
            if int(num)>=int(finalConfig['first_student']) \
                   and int(num)<=int(finalConfig['last_student']):
                verbose("filters matched",3)
                filteredRoster.append(student)
       
    verbose("final filtered roster is {} rows".format(len(filteredRoster)),3)
    for student in filteredRoster: verbose(student['login'],3)
    return(filteredRoster)         
        
##get ready
# get cmdline options
args=vars(getopts(sys.argv))
verbose('\n'.join(['Command line options, including defaults','\n'.join('{}={}'.format(key, val) for key, val in args.items())]),2)



#synthesize command line options for grouped shortcuts
if args['setup'] is True:
    args['activate']=True
    args['reset_apikey'] = True
    args['print_roster'] = True
if args['shutdown'] is True:
    args['deactivate'] = True
    args['reset_apikey'] = True

#deal with side cases where we don't even need the config file
if args['rtfm'] is True:
     verbose('--rtfm found on command line, printing doc link and exiting')
     print('https://panacea.threatgrid.com/mask/#/doc/main/account-management-api.html')
     exit()
#sanity checking
if args['setup'] is True and args['shutdown'] is True:
    print ('Both --setup and --shutdown were specified on the command line. No. Just... no.')
    exit()
if args['activate'] is True and args['deactivate'] is True:
    print('I\'m not going to activate and also deactivate the same users. Make up your mind or call with -h for usage help')
    exit()


    
if not (args['activate'] or args['deactivate'] or args['make_users'] or args['reset_apikey'] or args['print_roster'] \
        or args['print_deep_roster'] or args['nuke_from_orbit'] or args['password'] or args['sample_limit'] or args['delete_users']):
    print('Nothing to do! Call with -h for usage help. Exiting.')
    exit()

# Read config file to get settings
verbose('reading config file '+args['cfg_file'].name)
config = configparser.RawConfigParser()
config.read(args['cfg_file'].name)

#get all the main config
mainConfig=dict(config.items('PROGRAM'))

#get all the class config
classConfig=dict(config.items('CLASS'))

#get all the server config
serverConfig=dict(config.items('SERVER'))

#glom together
finalConfig=mainConfig.copy()
finalConfig.update(classConfig)
finalConfig.update(serverConfig)

#overwrite config file args with cmdline args where applicable
for key,val in args.items():
    if val is not None:
        finalConfig[key]=val

verbose('\n'.join(['Final config, including defaults','\n'.join('{}={}'.format(key, val) for key, val in finalConfig.items())]),2)

#check for API key
if finalConfig['api_key'] is None or len(finalConfig['api_key']) != 26 :
    print('''No API key or invalid API key - this won't work. Exiting.''')
    exit()

##do some preliminary construction
#make reusable root path
finalConfig['root_path']='https://'+finalConfig['server_name']+finalConfig['api_path']
#get orgID
orgID=str(getOrgID())
verbose('Retreived orgID of '+orgID)
 
##do the thing(s)

#if spec'd, delete all students
if finalConfig['nuke_from_orbit'] is True:
    finalConfig['print_roster'] = True
    #delete all students
    data='{"api_key": "'+finalConfig['api_key']+'"}'
    for student in getRoster():
        url=finalConfig['root_path']+finalConfig['user_path']+'/'+student['login']
        verbose('deleting user '+student['login']+' via DELETE to '+url)
        if finalConfig['experiment'] is not True:
            r=mydelete(url, data)
            print(r)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint request would have been a DELETE to '+url+' with parameters: '+data)

#if spec'd, delete some students
if finalConfig['delete_users'] is True:
    deletionList=getFilteredRoster()
    verbose("deleting "+finalConfig['num_students']+" accounts, from "+finalConfig['first_student']+" to "+finalConfig['last_student'])
    for student in getFilteredRoster():
        url=finalConfig['root_path']+finalConfig['user_path']+'/'+thisStudent['login']
        verbose('deleting user '+student['login']+' via DELETE to '+url)
        if finalConfig['experiment'] is not True:
            r=mydelete(url, data)
            print(r)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint request would have been a DELETE to '+url+' with parameters: '+data) 

            
#if spec'd, make users
if finalConfig['make_users'] is True:
    getStudentRange()
    print('Creating '+finalConfig['num_students']+' student accounts with name prefix '+finalConfig['username_prefix']+'.')
    #prepare loop
    if 'pad_length' not in finalConfig: #if not spec'd default to max len of range
        finalConfig['pad_length']=len(finalConfig['last_student'])
    int_num_students = int(finalConfig['num_students'])
    int_num_thisStudent=int(finalConfig['first_student'])
    int_num_lastStudent=int(finalConfig['last_student'])
    thisStudentData=dict()
    thisStudentData['api_key']=finalConfig['api_key']
    #for each student, build and make the request
    while int_num_thisStudent <= int_num_lastStudent:
        thisStudentData['title']=finalConfig['username_prefix']
        thisStudentData['login']=finalConfig['username_prefix']+str(int_num_thisStudent).zfill(int(finalConfig['pad_length']))
        thisStudentData['name']=thisStudentData['login']
        thisStudentData['email']=finalConfig['instructor_email'].replace('@',''.join(['+',thisStudentData['login'],'@']))
        if thisStudentData['email'].startswith('+'):thisStudentData['email']=thisStudentData['login']+finalConfig['instructor_email']
        #make the actual POST JSON
        postdata=json.dumps(thisStudentData)
        #talk too much
        verbose(' '.join(['this student is number', str(int_num_thisStudent).zfill(int(finalConfig['pad_length']))]),2)
        verbose('\n'.join(['user dict contents','\n'.join('{}={}'.format(key, val) for key, val in thisStudentData.items())]),2)
        verbose('\n'.join(['final JSON:',postdata]),3)
        #make request
        if finalConfig['experiment'] is not True:
            result=mypost(finalConfig['root_path']+finalConfig['org_path']+'/'+orgID+'/users', postdata)
            print(result)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint requested would have been '+finalConfig['root_path']+finalConfig['org_path']+'/'+orgID+'/users'+' with post data of '+postdata) 
        int_num_thisStudent=int_num_thisStudent+1
    print('Done.')
    
#if spec'd, activate or deactivate users
if finalConfig['activate'] is True or finalConfig['deactivate'] is True:
    data='{"api_key": "'+finalConfig['api_key']+'"}'
    if finalConfig['activate'] is True:
        action=['activate', 'PUT']
    else:
        action=['de-activate', 'DELETE']
    getStudentRange()
    print('preparing to '+action[0]+' '+finalConfig['num_students']+" accounts, from "+finalConfig['first_student']+" to "+finalConfig['last_student'])
    for student in getFilteredRoster():
        url=finalConfig['root_path']+finalConfig['user_path']+'/'+student['login']+'/active'
        verbose('prepared to '+action[0]+' '+student['login']+' via '+action[1]+' request to url '+url+' with data '+data,2)
        if finalConfig['experiment'] is not True:
            if action[0] == 'activate':
                r=myput(url, data)
            else:
                r=mydelete(url, data)
            verbose('server response is: '+r,2)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint request would have been a '+action[1]+' to '+url+' with post data of '+data)
    print('Done.')
    
#if spec'd, reset users' API keys
if finalConfig['reset_apikey'] is True:
    print('resetting student API keys')
    data='{"api_key": "'+finalConfig['api_key']+'"}'      
    for student in getFilteredRoster():
        url=finalConfig['root_path']+finalConfig['user_path']+'/'+student['login']+'/api-key'
        verbose('prepared to reset api key for '+student['login']+' via PUT to  url '+url+' with data '+data,2)
        if finalConfig['experiment'] is not True:
            r=myput(url, data)
            verbose('server response is: '+r,2)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint request would have been a PUT to '+url+' with post data of '+data)
    print('Done.')
               
#if spec'd, set passwords
if finalConfig['password']:
    print('changing student passwords')
        
    for student in getFilteredRoster():
        url=finalConfig['root_path']+finalConfig['user_path']+'/'+student['login']+'/password'
        data='{"api_key": "'+finalConfig['api_key']+'", "password": "'+finalConfig['password']+'"}'
        verbose('prepared to set password for '+student['login']+' to '+finalConfig['password']+' via PUT to  url '+url+' with data '+data,2)
        if finalConfig['experiment'] is not True:
            r=myput(url, data)
            print(r)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint request would have been a PUT to '+url+' with post data of '+data)
    print('Done.')

       
#if spec'd, set sample rate limit
if finalConfig['sample_limit']:
    print('setting daily sample rates')
    for student in getFilteredRoster():
        url=finalConfig['root_path']+finalConfig['user_path']+'/'+student['login']+'/rate-limit'
        data='{"api_key": "'+finalConfig['api_key']+'", "submission-rate-limit": [['+finalConfig['sample_limit']+',1440]]}'
        verbose('prepared to set daily sample limit for '+student['login']+' to '+finalConfig['sample_limit']+' via PUT to  url '+url+' with data '+data,2)
        if finalConfig['experiment'] is not True:
            r=myput(url, data)
            print(r)
        else:
            print('not calling the API because -x/--experiment was set at the command line.')
            print('API endpoint request would have been a PUT to '+url+' with post data of '+data)
    print('Done.')   

#if spec'd, print detailed class roster
if finalConfig['print_deep_roster'] is True:
    print('printing detailed roster')
    getStudentRange()
    #make header row pretty :/
    pad=' '*(len(finalConfig['username_prefix'])+len(finalConfig['num_students'])-len('STUDENT_LOGIN'))
    print('\n'+pad+'\t'.join(['LOGIN','NAME','EMAIL', 'TITLE', 'ROLE', 'ACTIVE', 'API_KEY', 'PROPERTIES'])+'\n')
    #print row per student, double spaced
    for student in getFilteredRoster():
        print ('\t'.join([student['login'], student['name'], student['email'], student['title'], student['role'], str(student['active']), student['api_key'], \
                            '{'+' '.join('{}: {}'.format(str(k),str(v)) for k,v in student['properties'].items())+' }']))
        
#if spec'd, print class roster
if finalConfig['print_roster'] is True:
    print('printing roster')
    #make header row pretty :/
    pad=' '*(len(finalConfig['username_prefix'])+len(finalConfig['num_students'])-len('STUDENT_LOGIN'))
    print('\n'+pad+'STUDENT_LOGIN\t\tAPI_KEY\t\tACTIVE?'+'\n')
    #print row per student, double spaced
    for student in getFilteredRoster():
        print (student['login']+'\t\t'+student['api_key']+'\t\t'+str(student['active'])+'\n')
        
exit()


