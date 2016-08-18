"""
imaptools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

imaptools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with imaptools. If not, see <http://www.gnu.org/licenses/>.


Copyright (c) 2013 Vicente Ruiz <vruiz2.0@gmail.com>
"""
import argparse
import email
import imaplib
import mailbox
import re
import sys
from imaplib import IMAP4, IMAP4_SSL
from textwrap import TextWrapper


class IMAPTool(object):
    def __init__(self, server, port=None, ssl=False):
        IMAP = IMAP4 if not ssl else IMAP4_SSL
        # Selecting the port
        if port is None:
            port = imaplib.IMAP4_PORT if not ssl else imaplib.IMAP4_SSL_PORT
        # Creating server connection
        self.server = IMAP(server, port)

    def login(self, email, password):
        self.server.login(email, password)

    def logout(self):
        self.server.logout()

    def close(self):
        self.server.close()

    def get_folders(self):
        folders = []
        foldptn = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

        for fold_desc in self.server.list()[1]:
            flags, delimiter, folder = foldptn.match(fold_desc.decode('iso-8859-1')).groups()
            if folder.startswith('"'):
                folder = folder[1:]
            if folder.endswith('"'):
                folder = folder[:-1]
            folders.append(folder)
        return folders

    def backup_folder(self, folder):
        print('Backup:', folder)
        folder_name = '"%s"' % folder
        resp, info = self.server.select(folder_name)
        if resp != 'OK':
            raise IMAP4.error(info)

        filename = folder.replace('/', '.') + '.mbox'

        mbox = open(filename, 'w')
        resp, items = self.server.search(None, "ALL")
        numbers = items[0].split()
        for num in numbers:
            resp, data = self.server.fetch(num, "(BODY.PEEK[])")
            text = data[0][1].decode('iso-8859-1')
            message = email.message_from_string(text)
            mbox.write(message.as_string(unixfrom=True))
        mbox.close()

    def backup(self):
        """Create a backup of all folders of logged user account"""
        folders = self.get_folders()
        for folder in folders:
            self.backup_folder(folder)

    def restore_mbox(self, path, folder=None):
        filename = path.split('/')[-1]
        if folder is None:
            parts = filename.split('.')
            if parts[-1] != 'mbox':
                folder = filename
            else:
                folder = '.'.join(parts[:-1])

        self.server.create(folder)
        self.server.select(folder)

        mbox = mailbox.mbox(path)
        #message_set.lock() # Be careful with exceptions

        for message in mbox:
            self.server.append(folder, None, None, str(message).encode('utf-8'))

        #message_set.unlock()
        mbox.close()



if __name__ == '__main__':
    from getpass import getpass

    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="mail server name")
    parser.add_argument('-P', '--port', type=int, help="mail server port")
    parser.add_argument('--ssl', action='store_true', default=False, help="use SSL")
    parser.add_argument('email', help="username or email")
    parser.add_argument('-p', '--password', dest='password', help="password")
    subparsers = parser.add_subparsers(dest='action', help='action-command help')

    # create the parser for the "test" command
    parser_test = subparsers.add_parser('test', help='test help')
    parser_test.add_argument('action', type=str, choices=('connection', 'account'))

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='list help')

    # create the parser for the "backup" command
    parser_backup = subparsers.add_parser('backup', help='backup help')
    parser_backup.add_argument('folders', metavar='folder', type=str, nargs='*')

    # create the parser for the "restore" command
    parser_restore = subparsers.add_parser('restore', help='restore help')
    parser_restore.add_argument('mboxes', metavar='mbox', type=str, nargs='+')

    args = vars(parser.parse_args())

    # Checking if password option is present
    if args['password'] is None:
        args['password'] = getpass()

    tool = IMAPTool(args['server'], args['port'], args['ssl'])
    tool.login(args['email'], args['password'])

    if args['action'] == 'test':
        pass
    elif args['action'] == 'list':
        for folder in tool.get_folders():
            print(folder)
    elif args['action'] == 'backup':
        # Getting the folder list
        folders = args['folders']
        if not folders:
            folders = tool.get_folders()
        # Backup the selected folders
        for folder in folders:
            print('Backing up:', folder)
            tool.backup_folder(folder)
    elif args['action'] == 'restore':
        # Getting the mbox list
        mboxes = args['mboxes']
        for mbox in mboxes:
            print('Restoring:', mbox)
            tool.restore_mbox(mbox)

    tool.logout()
    #tool.close()
