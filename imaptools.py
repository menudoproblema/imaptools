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
import imaplib
import re
import sys
from email.parser import Parser
from imaplib import IMAP4, IMAP4_SSL
from textwrap import TextWrapper


class IMAPTool(object):
    def __init__(self, server, port=None, ssl=False):
        IMAP = IMAP4 if not ssl else IMAP4_SSL
        
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
        foldptn = re.compile('\([^\)]*\) "[^"]*" "([^"]*)"')
        
        for fold_desc in self.server.list()[1]:
            folder = foldptn.sub(r'\1', fold_desc.decode('iso-8859-1'))
            folders.append(folder)
        
        return folders
    
    def backup_folder(self, folder):
        folder = '"%s"' % folder
        parser = Parser()
        resp, info = self.server.select(folder)
        if resp != 'OK':
            raise IMAP4.error(info)

        filename = folder.replace('/', '.') + '.mbox'
        
        mbox = open(filename, 'w')
        resp, items = self.server.search(None, "ALL")
        numbers = items[0].split()
        for num in numbers:
            resp, data = self.server.fetch(num, "(BODY.PEEK[])")
            text = data[0][1].decode('iso-8859-1')
            message = parser.parsestr(text)
            mbox.write(message.as_string(unixfrom=True))
        mbox.close()
    
    def backup(self):
        """Create a backup of all folders of logged user account"""
        folders = self.get_folders()
        for folder in folders:
            self.backup_folder(folder)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="Mail server name")
    parser.add_argument('-P', '--port', type=int, help="Mail server port")
    parser.add_argument('--ssl', action='store_true', default=False, help="Use SSL")
    parser.add_argument('-u', '--username', dest='email', help="Username or email")
    parser.add_argument('-p', '--password', dest='password', help="Password")
    args = vars(parser.parse_args())
    
    tool = IMAPTool(args['server'], args['port'], args['ssl'])
    tool.login(args['email'], args['password'])
    folders = tool.get_folders()
    for folder in folders:
        print(folder)
        tool.backup_folder(folder)


