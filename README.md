imaptools
=========

Tools for test/backup/restore imap accounts

`Note` Tested on Python 3

Usage
-----

    $ python3 imaptools.py --help
    usage: imaptools.py [-h] [-P PORT] [--ssl] [-p PASSWORD]
                    server email {test,list,backup,restore} ...

    positional arguments:
      server                mail server name
      email                 username or email
      {test,list,backup,restore}
                            action-command help
        test                test help
        list                list help
        backup              backup help
        restore             restore help

    optional arguments:
      -h, --help            show this help message and exit
      -P PORT, --port PORT  mail server port
      --ssl                 use SSL
      -p PASSWORD, --password PASSWORD
                            password

