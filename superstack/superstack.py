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
import ConfigParser
import keyring
import os
import re
import subprocess
import sys


class SuperStack:

    def __init__(self):
        self.stack_creds = None
        self.stack_env = None
        self.env = os.environ.copy()

    def check_deprecated_options(self):
        """
        Hunts for deprecated configuration options from previous SuperStack
        versions.
        """
        creds = self.get_stack_creds()
        if creds.has_option(self.stack_env, 'insecure'):
            print "WARNING: the 'insecure' option is deprecated. " \
                  "Consider using OS_CLIENT_INSECURE=1 instead."

    def get_stack_creds(self):
        """
        Reads the superstack config file from the current directory or the
        user's home directory.  If the config file has already been read, the
        cached copy is immediately returned.
        """
        if self.stack_creds:
            return self.stack_creds

        possible_configs = [os.path.expanduser("~/.superstack"), '.superstack']
        self.stack_creds = ConfigParser.RawConfigParser()
        self.stack_creds.read(possible_configs)
        if len(self.stack_creds.sections()) < 1:
            return None
        return self.stack_creds

    def is_valid_environment(self):
        """
        Checks to see if the configuration file contains a section for our
        requested environment.
        """
        valid_envs = self.get_stack_creds().sections()
        return self.stack_env in valid_envs

    def password_get(self, username=None):
        """
        Retrieves a password from the keychain based on the environment and
        configuration parameter pair.
        """
        try:
            return keyring.get_password('superstack', username)
        except:
            return False

    def password_set(self, username=None, password=None):
        """
        Stores a password in a keychain for a particular environment and
        configuration parameter pair.
        """
        try:
            keyring.set_password('superstack', username, password)
            return True
        except:
            return False

    def prep_stack_creds(self):
        """
        Finds relevant config options in the superstack config and cleans them
        up for openstack client.
        """
        self.check_deprecated_options()
        raw_creds = self.get_stack_creds().items(self.stack_env)
        stack_re = re.compile(r"(^stack_|^os_|^openstack)")

        creds = []
        for param, value in raw_creds:

            # Skip parameters we're unfamiliar with
            if not stack_re.match(param):
                continue

            param = param.upper()

            # Get values from the keyring if we find a USE_KEYRING constant
            if value.startswith("USE_KEYRING"):
                rex = "USE_KEYRING\[([\x27\x22])(.*)\\1\]"
                if value == "USE_KEYRING":
                    username = "%s:%s" % (self.stack_env, param)
                else:
                    global_identifier = re.match(rex, value).group(2)
                    username = "%s:%s" % ('global', global_identifier)
                credential = self.password_get(username)
            else:
                credential = value.strip("\"'")

            # Make sure we got something valid from the configuration file or
            # the keyring
            if not credential:
                msg = "Attempted to retrieve a credential for %s but " \
                      "couldn't find it within the keyring." % username
                raise Exception(msg)

            creds.append((param, credential))

        return creds

    def prep_shell_environment(self):
        """
        Appends new variables to the current shell environment temporarily.
        """
        for k, v in self.prep_stack_creds():
            self.env[k] = v

    def run_openstackclient(self, stack_args, force_debug=False):
        """
        Sets the environment variables for openstack client, runs
        openstack client, and prints the output.
        """
        # Get the environment variables ready
        self.prep_shell_environment()

        # Check for a debug override
        if force_debug:
            stack_args.insert(0, '--debug')

        # Call openstack client and connect stdout/stderr to the current
        # terminal so that any unicode characters from openstack client's list
        # will be displayed appropriately.
        #
        # In other news, I hate how python 2.6 does unicode.
        p = subprocess.Popen(['openstack'] + stack_args,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=self.env
        )

        # Don't exit until we're sure the subprocess has exited
        p.wait()
