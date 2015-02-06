#!/usr/bin/env python
#
# Copyright 2012 Major Hayden
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import getpass
import argparse
import superstack
import sys


def gwrap(some_string):
    """
    Returns green text
    """
    return "\033[92m%s\033[0m" % some_string


def rwrap(some_string):
    """
    Returns red text
    """
    return "\033[91m%s\033[0m" % some_string


def print_valid_envs(valid_envs):
    """
    Prints the available environments.
    """
    print "[%s] Your valid environments are:" % (gwrap('Found environments'))
    print "%r" % valid_envs


def check_superstack_conf(s):
    """Checks to make sure superstack can read it's config file."""
    if s.get_stack_creds() is None:
        msg = ('[%s] Unable to find your superstack configuration file or your '
               'configuration file is malformed.')
        print msg % rwrap('Configuration missing')
        sys.exit()


def setup_superstack_env(s, env):
    """Set superstack object's stack_env and ensure validity."""
    s.stack_env = env
    if not s.is_valid_environment():
        msg = ('[%s] Unable to find the %r environment in your '
               'configuration file.')
        print msg % (rwrap('Invalid environment'), env)
        print_valid_envs(sorted(s.get_stack_creds().sections()))
        sys.exit()


# Note(tr3buchet): this is necessary to prevent argparse from requiring the
#                  the 'env' parameter when using -l or --list
class _ListAction(argparse._HelpAction):
    """ListAction used for the -l and --list arguments."""
    def __call__(self, parser, *args, **kwargs):
        """Lists are configured superstack environments."""
        s = superstack.SuperStack()
        for stack_env in s.get_stack_creds().sections():
            envheader = '-- %s ' % gwrap(stack_env)
            print envheader.ljust(86, '-')
            for param, value in sorted(s.get_stack_creds().items(stack_env)):
                print '  %s: %s' % (param.upper().ljust(21), value)
        parser.exit()


def run_superstack():
    """
    Handles all of the prep work and error checking for the
    superstack executable.
    """
    s = superstack.SuperStack()
    check_superstack_conf(s)

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action=_ListAction,
                        dest='listenvs',
                        help='list all configured environments')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='show openstack client debug output')
    parser.add_argument('env',
                        help=('environment to run openstack against. '
                              'valid options: %s' %
                              sorted(s.get_stack_creds().sections())))

    # Allow for passing --options all the way through to openstack client
    superstack_args, stack_args = parser.parse_known_args()

    # Did we get any arguments to pass on to openstack?
    if not stack_args:
        msg = '[%s] No arguments were provided to pass along to openstack.'
        print msg % rwrap('Missing openstack client arguments')
        sys.exit()

    setup_superstack_env(s, superstack_args.env)

    # All of the remaining arguments should be handed off to openstack
    s.run_openstackclient(stack_args, superstack_args.debug)


def run_superstack_keyring():
    """
    Handles all of the prep work and error checking for the
    superstack-keyring executable.
    """
    s = superstack.SuperStack()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--get', action='store_true',
                       dest='get_password',
                       help='retrieves credentials from keychain storage')
    group.add_argument('-s', '--set', action='store_true',
                       dest='set_password',
                       help='stores credentials in keychain storage')
    parser.add_argument('env',
                        help='environment to set parameter in')
    parser.add_argument('parameter',
                        help='parameter to set')
    args = parser.parse_args()

    username = '%s:%s' % (args.env, args.parameter)

    if args.set_password:
        print "[%s] Preparing to set a password in the keyring for:" % (
            gwrap("Keyring operation"))
        print "  - Environment  : %s" % args.env
        print "  - Par ameter    : %s" % args.parameter
        print "\n  If this is correct, enter the corresponding credential " \
              "to store in \n  your keyring or press CTRL-D to abort: ",

        # Prompt for a password and catch a CTRL-D
        try:
            password = getpass.getpass('')
        except:
            password = None
            print

        # Did we get a password from the prompt?
        if not password or len(password) < 1:
            print "\n[%s] No data was altered in your keyring." % (
                rwrap("Canceled"))
            sys.exit()

        # Try to store the password
        try:
            store_ok = s.password_set(username, password)
        except:
            store_ok = False

        if store_ok:
            print "\n[%s] Successfully stored credentials for %s under the " \
                  "superstack service." % (gwrap("Success"), username)
        else:
            print "\n[%s] Unable to store credentials for %s under the " \
                  "superstack service." % (rwrap("Failed"), username)

        sys.exit()

    if args.get_password:
        print "[%s] If this operation is successful, the credential " \
              "stored \nfor %s will be displayed in your terminal as " \
              "plain text." % (rwrap("Warning"), username)
        print "\nIf you really want to proceed, type yes and press enter:",
        confirm = raw_input('')

        if confirm != 'yes':
            print "\n[%s] Your keyring was not read or altered." % (
                rwrap("Canceled"))
            sys.exit()

        try:
            password = s.password_get(username)
        except:
            password = None

        if password:
            print "\n[%s] Found credentials for %s: %s" % (
                gwrap("Success"), username, password)
        else:
            print "\n[%s] Unable to retrieve credentials for %s.\nThere are " \
                "probably no credentials stored for this environment/" \
                "parameter combination (try --set)." % (
                    rwrap("Failed"), username)
