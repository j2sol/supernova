## superstack - use openstack client with multiple openstack environments the easy way

You may like *superstack* if you regularly have the following problems:

* You hate trying to source multiple stackrc files when using *openstack*
* You get your terminals confused and do the wrong things in the wrong openstack environment
* You don't like remembering things
* You want to keep sensitive API keys and passwords out of plain text configuration files (see the "Working with keyrings" section toward the end)
* You need to share common skeleton environment variables for *openstack* with your teams

If any of these complaints ring true, *superstack* is for you. *superstack* manages multiple openstack environments without sourcing stackrc's or mucking with environment variables.

![First world problems - openstack style](http://lolcdn.mhtx.net/firstworldproblems-multiplenovaenvironments-20120316-072224.jpg)

### Installation

    git clone git://github.com/j2sol/superstack.git
    cd superstack
    python setup.py install

### Configuration

For *superstack* to work properly, each environment must be defined in `~/.superstack` (in your user's home directory).  The data in the file is exactly the same as the environment variables which you would normally use when running *openstack*.  You can copy/paste from your stackrc files directly into configuration sections within `~/.superstack`.

Here's an example of two environments, **production** and **development**:

    [production]
    OS_AUTH_URL = http://production.stack.example.com:8774/v1.1/
    OS_USERNAME = jsmith
    OS_PASSWORD = fd62afe2-4686-469f-9849-ceaa792c55a6
    OS_TENANT_NAME = stack-production

    [development]
    OS_AUTH_URL = http://dev.stack.example.com:8774/v1.1/
    OS_USERNAME = jsmith
    OS_PASSWORD = 40318069-6069-4d9f-836d-a46df17fc8d1
    OS_TENANT_NAME = stack-development

When you use *superstack*, you'll refer to these environments as **production** and **development**.  Every environment is specified by its configuration header name.

### Usage

    superstack [--debug] [--list] [environment] [openstack client arguments...]

    Options:
    -h, --help   show this help message and exit
    -d, --debug  show oppenstack client debug output (overrides OSCLIENT_DEBUG)
    -l, --list   list all configured environments

##### Passing commands to *openstack*

For example, if you wanted to list all instances within the **production** environment:

    superstack production server list

Show a particular instance's data in the preprod environment:

    superstack preprod server show 3edb6dac-5a75-486a-be1b-3b15fd5b4ab0a

The first argument is generally the environment argument and it is expected to be a single word without spaces. Any text after the environment argument is passed directly to *openstack*.

##### Debug override

You may optionally pass `--debug` as the first argument (before the environment argument) to see additional debug information about the requests being made to the API:

    superstack --debug production server list

As before, any text after the environment argument is passed directly to *openstack*.

##### Listing your configured environments

You can list all of your configured environments by using the `--list` argument.

### Working with keyrings
Due to security policies at certain companies or due to general paranoia, some users may not want API keys or passwords stored in a plaintext *superstack* configuration file.  Luckily, support is now available (via the [keyring](http://pypi.python.org/pypi/keyring) module) for storing any configuration value within your operating system's keychain.  This has been tested on the following platforms:

* Mac: Keychain Access.app
* Linux: gnome-keyring, kwallet (keyring will determine the backend to use based on the system type and configuration. Make sure if you're using linux without Gnome/KDE that you have pycrypto and simplejson/json installed so CryptedFileKeyring is supported or you end up with UncryptedFileKeyring and your keyring won't be encrypted)

To get started, you'll need to choose an environment and a configuration option.  Here's an example of some data you might not want to keep in plain text:

    superstack-keyring --set production OS_PASSWORD

**TIP**: If you need to use the same data for multiple environments, you can use a global credential item very easily:

    superstack-keyring --set global MyCompanySSO

Once it's stored, you can test a retrieval:

    # Normal, per-environment storage
    superstack-keyring --get production OS_PASSWORD

    # Global storage
    superstack-keyring --get global MyCompanySSO

You'll need to confirm that you want the data from your keychain displayed in plain text (to hopefully thwart shoulder surfers).

Once you've stored your sensitive data, simply adjust your *superstack* configuration file:

    #OS_PASSWORD = really_sensitive_api_key_here
    
    # If using storage per environment
    OS_PASSWORD = USE_KEYRING
    
    # If using global storage
    OS_PASSWORD = USE_KEYRING['MyCompanySSO']

When *superstack* reads your configuration file and spots a value of `USE_KEYRING`, it will look for credentials stored under `OS_PASSWORD` for that environment automatically.  If your keyring doesn't have a corresponding credential, you'll get an exception.

#### A brief note about environment variables

*superstack* will only replace and/or append environment variables to the already present variables for the duration of the *openstack* execution. If you have `OS_USERNAME` set outside the script, it won't be used in the script since the script will pull data from `~/.superstack` and use it to run *openstack*. In addition, any variables which are set prior to running *superstack* will be left unaltered when the script exits.
