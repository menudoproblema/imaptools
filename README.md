imaptools
=========

Tools for test/backup/restore imap accounts

`Note` Tested on Python 3

Examples
--------

    $ python3 imaptools.py --help
    usage: imaptools.py [-h] [-P PORT] [--ssl] [-u EMAIL] [-p PASSWORD] server

    positional arguments:
      server                Mail server name

    optional arguments:
      -h, --help            show this help message and exit
      -P PORT, --port PORT  Mail server port
      --ssl                 Use SSL
      -u EMAIL, --username EMAIL
                            Username or email
      -p PASSWORD, --password PASSWORD
                            Password
