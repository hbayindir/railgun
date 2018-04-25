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
DEFAULT_CONFIGURATION_FILE_PATH = '../conf/railgun.conf'
LOGGING_LEVEL = logging.WARN

# This is our new Railgun class, which allows the application to be used as a library too.
class Railgun:
    
    # Let's put a small constructor here.
    def __init__ (self, configurationFilePath = DEFAULT_CONFIGURATION_FILE_PATH):
        # Root dictionary.
        self.options = dict ()
        
        # Logging options.
        self.options['logging'] = dict ()
        self.options['logging']['log_file_path'] = None
        
        # Mailgun API options.
        self.options['mailgun_api'] = dict()
        self.options['mailgun_api']['base_uri'] = None
        self.options['mailgun_api']['api_key'] = None
        
        # Mailgun API sender options.
        self.options['sender'] = dict()
        self.options['sender']['name'] = None
        self.options['sender']['email_address'] = None

        # Mail recipient (one for now)
        self.options['recipients'] = dict()
        self.options['recipients']['email_address'] = None
        
        # Parse the configuration file here.
        self.__parseConfigurationFile(configurationFilePath)
        self.__checkConfigurationSanity()
    
    def __parseConfigurationFile(self, configurationFilePath):
        # Let's read this little file.
        self.configuration = configparser.ConfigParser ()
        self.configuration.read(DEFAULT_CONFIGURATION_FILE_PATH)
    
        # These loops iterate over the configuration options.
        # This method is implemented to prevent code from attacks.
        for sectionKey in self.options.keys ():
            for optionKey in self.options[sectionKey].keys ():
                try:
                    self.options[sectionKey][optionKey] = self.configuration[sectionKey][optionKey]
                # Handle missing keys gracefully here.
                except KeyError as exception:
                    pass
    
    # This function checks whether the minimum requirements for railgun configuration is met.
    def __checkConfigurationSanity (self):

        if self.options['mailgun_api']['base_uri'] == None:
            raise Exception ('base_uri value of [mailgun_api] section cannot be None or missing. Please obtain the value for your domain from Mail Gun dashboard.')
    
        if self.options['mailgun_api']['api_key'] == None:
            raise Exception ('api_key value of [mailgun_api] section cannot be None or missing. Please obtain the value for your domain from Mail Gun dashboard.')
    
        if self.options['sender']['name'] == None:
            raise Exception ('name value of [sender] section cannot be None or missing. Please fill this value with a descriptive name for the sender.')
    
        if self.options['sender']['email_address'] == None:
            raise Exception ('email_address value of [sender] section cannot be None or missing. Please fill this value with a descriptive email address for the sender.')
    
        if self.options['recipients']['email_address'] == None:
            raise Exception ('email_address value of [recipients] section cannot be None or missing. Please fill this value with the email address for the intended receiver of the email.')


def sendTextEmail(subject, body, configuration):

    mailSender = configuration['sender']['name'] + ' <' + configuration['sender']['email_address'] + '>'

    return requests.post(
        configuration['mailgun_api']['base_uri'] + '/messages',
        auth=('api', configuration['mailgun_api']['api_key']),
        data={'from': mailSender,
              'to': configuration['recipients']['email_address'],
              'subject': subject,
              'text': body})

# Everything starts from this point.
if __name__ == '__main__':

    # Let's start with parsing the configuration file.
    # Check the file's existence first.
    if os.path.isfile(DEFAULT_CONFIGURATION_FILE_PATH) == False:
        print ('FATAL: Configuration file ' + DEFAULT_CONFIGURATION_FILE_PATH + ' is not present, exiting.', file = sys.stderr)
        sys.exit (1)

    try:
        railgun = Railgun ()
    except Exception as exception:
        print ('An exception has ocurred: ' + str(exception), file=sys.stderr)
        print ('Please correct above errors and restart railgun.', file=sys.stderr)
        sys.exit(1)
        

    # Let's parse some arguments.
    argumentParser = argparse.ArgumentParser()

    argumentParser.add_argument ('subject', metavar = 'SUBJECT', help = 'Subject of the e-mail to be sent.')
    argumentParser.add_argument ('body', metavar = 'BODY', help = 'Body of the e-mail to be sent.')
    
    verbosityGroup = argumentParser.add_mutually_exclusive_group()
    verbosityGroup.add_argument ('-v', '--verbose', help = 'Print more detail about the process. Using more than one -v increases verbosity.', action = 'count')
    verbosityGroup.add_argument ('-q', '--quiet', help = 'Do not print anything to console (overrides verbose).', action = 'store_true')

    # Version always comes last.
    argumentParser.add_argument ('-V', '--version', help = 'Print ' + argumentParser.prog + ' version and exit.', action = 'version', version = argumentParser.prog + ' version 1.0.3')    

    arguments = argumentParser.parse_args()

    if arguments.verbose == None:
        arguments.verbose = 0;

    # At this point we have the required arguments, let's start with logging duties.
    if arguments.verbose != None :
        if arguments.verbose == 1:
            LOGGING_LEVEL = logging.INFO
        elif arguments.verbose >= 2:
            LOGGING_LEVEL = logging.DEBUG

    # Let's set the logger up.
    try:
        logging.basicConfig(filename = railgun.options['logging']['log_file_path'], level = LOGGING_LEVEL, format = '%(levelname)s: %(message)s')

        # Get the local logger and start.
        localLogger = logging.getLogger('main')
        
        # Handle the quiet switch here, since it directly affects the logger.
        if arguments.quiet == True:
            logging.disable(logging.CRITICAL) # Critical is the highest built-in level. This line disables CRITICAL and below.

        localLogger.debug('Logger setup completed.')
        localLogger.debug('%s is starting.', sys.argv[0])
    except IOError as exception:
        print ('Something about disk I/O went bad: ' + str(exception), file = sys.stderr)
        sys.exit(1)

    # Let's write some debugging information
    localLogger.debug ('Configuarion details:')
    localLogger.debug ('Logging file path: ' + str(railgun.options['logging']['log_file_path']) + '.')
    localLogger.debug ('Sending mails as: ' + str(railgun.options['sender']['name']) + ' <' + str(railgun.options['sender']['email_address']) + '>.')
    localLogger.debug ('Sending mails to: ' + str(railgun.options['recipients']['email_address']) + '.')

    # Setting up the application is complete. Just send the mail now.
    request = sendTextEmail(arguments.subject, arguments.body, railgun.options)

    if request.status_code == 200:
        localLogger.info ('The message has sent successfully.')
    else:
        localLogger.error ('Something went wrong. Error code is ' + request.status_code + '.')
