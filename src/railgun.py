#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Created on Feb 12, 2018

@author: Hakan Bayındır
@summary: Railgun: Send e-mails via MailGun from command line.
@license: GNU/GPLv3
'''

import os
import sys
import configparser
import logging
import argparse
import requests # This is how we talk with MailGun API.


# Some global constants. Change as you see fit.
CONFIGURATION_FILE_PATH = '../conf/railgun.conf'
LOGGING_LEVEL = logging.INFO

# Below are mailgun configuation options.
# Its modeled as a nested dictionary intentionally.
# Only these keys will be queried from the file.
# First, the logging options.
railgunOptions = dict ()
railgunOptions['logging'] = dict()
railgunOptions['logging']['log_file_path'] = None

# MailGun API options.
railgunOptions['mailgun_api'] = dict()
railgunOptions['mailgun_api']['base_uri'] = None
railgunOptions['mailgun_api']['api_key'] = None

# MailGun API sender options.
railgunOptions['sender'] = dict()
railgunOptions['sender']['name'] = None
railgunOptions['sender']['email_address'] = None

# Mail recipient (one for now)
railgunOptions['recipients'] = dict()
railgunOptions['recipients']['email_address'] = None


def sendSimpleMessage(subject, body):

    mailSender = railgunOptions['sender']['name'] + ' <' + railgunOptions['sender']['email_address'] + '>'

    return requests.post(
        railgunOptions['mailgun_api']['base_uri'] + '/messages',
        auth=('api', railgunOptions['mailgun_api']['api_key']),
        data={'from': mailSender,
              'to': railgunOptions['recipients']['email_address'],
              'subject': subject,
              'text': body})

# Everything starts from this point.
if __name__ == '__main__':

    # Let's start with parsing the configuration file.
    # Check the file's existence first.
    if os.path.isfile(CONFIGURATION_FILE_PATH) == False:
        print ('FATAL: Configuration file ' + CONFIGURATION_FILE_PATH + ' is not present, exiting.', file = sys.stderr)
        sys.exit (1)

    # Let's read this little file.
    configuration = configparser.ConfigParser ()
    configuration.read(CONFIGURATION_FILE_PATH)

    # These loops iterate over the configuration options.
    # This method is implemented to prevent code from attacks.
    for sectionKey in railgunOptions.keys ():
        for optionKey in railgunOptions[sectionKey].keys ():
            try:
                railgunOptions[sectionKey][optionKey] = configuration[sectionKey][optionKey]
            # Handle missing keys gracefully here.
            except KeyError as exception:
                pass

    # Let's set the logger up.
    try:
        logging.basicConfig(filename = railgunOptions['logging']['log_file_path'], level = LOGGING_LEVEL, format = '%(levelname)s: %(message)s')

        # Get the local logger and start.
        localLogger = logging.getLogger('main')

        localLogger.debug('Logger setup completed.')
        localLogger.debug('%s is starting.', sys.argv[0])
    except IOError as exception:
        print ('Something about disk I/O went bad: ' + str(exception), file = sys.stderr)
        sys.exit(1)

    # Let's make configuration sanity check. Some configuration options are mandatory. We cannot continue without them.
    isConfigurationSane = True

    if railgunOptions['mailgun_api']['base_uri'] == None:
        localLogger.critical ('base_uri value of [mailgun_api] section cannot be None or missing. Please obtain the value for your domain from Mail Gun dashboard.')
        isConfigurationSane = False

    if railgunOptions['mailgun_api']['api_key'] == None:
        localLogger.critical ('api_key value of [mailgun_api] section cannot be None or missing. Please obtain the value for your domain from Mail Gun dashboard.')
        isConfigurationSane = False

    if railgunOptions['sender']['name'] == None:
        localLogger.critical ('name value of [sender] section cannot be None or missing. Please fill this value with a descriptive name for the sender.')
        isConfigurationSane = False

    if railgunOptions['sender']['email_address'] == None:
        localLogger.critical ('email_address value of [sender] section cannot be None or missing. Please fill this value with a descriptive email address for the sender.')
        isConfigurationSane = False

    if railgunOptions['recipients']['email_address'] == None:
        localLogger.critical ('email_address value of [recipients] section cannot be None or missing. Please fill this value with the email address for the intended receiver of the email.')
        isConfigurationSane = False

    if isConfigurationSane == False:
        localLogger.critical ('Please correct the configuration errors above and restart ' + sys.argv[0])
        sys.exit (1)

    # Let's write some debugging information
    localLogger.debug ('Configuarion details:')
    localLogger.debug ('Logging file path: ' + str(railgunOptions['logging']['log_file_path']) + '.')
    localLogger.debug ('Sending mails as: ' + str(railgunOptions['sender']['name']) + ' <' + str(railgunOptions['sender']['email_address']) + '>.')
    localLogger.debug ('Sending mails to: ' + str(railgunOptions['recipients']['email_address']) + '.')

    # Let's parse some arguments.
    argumentParser = argparse.ArgumentParser()

    argumentParser.add_argument ('subject', metavar = 'SUBJECT', help = 'Subject of the e-mail to be sent.')
    argumentParser.add_argument ('body', metavar = 'BODY', help = 'Body of the e-mail to be sent.')

    # Version always comes last.
    argumentParser.add_argument ('-V', '--version', help = 'Print ' + argumentParser.prog + ' version and exit.', action = 'version', version = argumentParser.prog + ' version 1.0.0')    

    arguments = argumentParser.parse_args()


    # Setting up the application is complete. Just send the mail now.
    request = sendSimpleMessage(arguments.subject, arguments.body)

    if request.status_code == 200:
        localLogger.info ('The message has sent successfully.')
    else:
        localLogger.error ('Something went wrong. Error code is ' + request.status_code + '.')