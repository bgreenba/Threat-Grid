ANTI-TEDIUM: Automated iNtuitive Threatgrid Interactions - Total Educational Deployment In Under a Minute

This script can be used by Organization Administrators to automate the creation and management of student accounts in a dedicated classroom TG Organization. USE WITH CARE - It will take the requested action on all non-admin accounts in whatever organization is associated with the provided Admin API key.

Inspired by a need to set up and then tear down entire orgs used for training purposes and not wanting to click on four things to reset each of 50 student accounts. 
This is not a normal use case, and this script is provided here largely as an example of what can be done with the user management portions of the API.
The reset passwords bits might be useful to tie TG into your SSO provider. 



```
anti-tedium.py -h
usage: anti-tedium.py [-h] [-c CFG_FILE] [-l LOG_FILE] [-k API_KEY]
                      [-s SERVER_NAME] [-v] [-x] [-n NUM_STUDENTS]
                      [-u USERNAME_PREFIX]
                      [--instructor_email INSTRUCTOR_EMAIL] [--make_users]
                      [--nuke_from_orbit] [-a] [-d] [-r]
                      [--sample_limit SAMPLE_LIMIT] [-p PASSWORD]
                      [--print_roster] [--rtfm] [-1] [-0]



optional arguments:
  -h, --help            show this help message and exit

Configuration:
  Program and API configuration settings

  -c CFG_FILE, --cfg_file CFG_FILE
                        specify a configuration file (default anti-tedium.cfg)
  -l LOG_FILE, --log_file LOG_FILE
                        specify a log file (overrides config file)
  -k API_KEY, --api_key API_KEY
                        specify an API key value (overrides config file)
  -s SERVER_NAME, --server_name SERVER_NAME
                        specify a server hostname (overrides config file)
  -v, --verbose         print diagnostic and troubleshooting information to
                        stdout. Once for a reasonable amount, more for lots
                        (0-3)
  -x, --experiment      Do everything except request the changes. Most useful
                        with -v

User Options:
  Student account options

  -n NUM_STUDENTS, --num_students NUM_STUDENTS
                        specify number of student accounts to create
                        (overrides config file)
  -u USERNAME_PREFIX, --username_prefix USERNAME_PREFIX
                        prefix for user names [prefix01, prefix02,...
                        prefix(n)](overrides config file)
  --instructor_email INSTRUCTOR_EMAIL
                        set instructor email address. (overrides config file).
                        All student emails will be constructed out of this
                        information as follows: for an instructor address of
                        instructor@domain, all student emails will be set to
                        instructor+prefix(n)@domain

Account Actions:
  Actions to take on non-admin accounts

  --make_users          This will create users as specified in the config file
                        and cmdline parameters. This will be done prior to
                        activate, deactive, or reset actions.
  --nuke_from_orbit     Delete all student accounts. ALL of them, regardless
                        of prefix or supplied user count. When the nuke has
                        passed, only admins shall remain.
  -a, --activate        This will activate all non-admin users in the org
  -d, --deactivate      This will de-activate all non-admin users in the org
  -r, --reset_apikey    This will reset the API key for all non-admin users in
                        the org
  --sample_limit SAMPLE_LIMIT
                        This will set the sample limit per day for all non-
                        admin users. Follow it with a number.
  -p PASSWORD, --password PASSWORD
                        sets password for all non-admin accounts in the org
                        (UNTESTED)

Misc Actions:
  Actions that don't affect user accounts but do have an output

  --print_roster        print out a list of all non-admin accounts and their
                        corresponding API keys
  --rtfm                print a link to the API documentation for user
                        management and exit. (Threat Grid account required)

Setup and Shutdown batch actions:
  Shortcuts that set multiple actions

  -1, --setup           sets up classroom - sets all nonadmin accounts to
                        active, resets password and API keys, and prints
                        roster (shortcut for -ra --print_roster)
  -0, --shutdown        shuts down classroom - sets all non-admin accounts to
                        inactive and resets their API keys (shortcut for -rd)



```
