from argparse import ArgumentParser

from services.create_timelines import *
from utils.settings_creator import create_settings_file, travis_setup

from manage_db import (connect, create_tables, migrate)

from manage_user import (create_user)

parser = ArgumentParser()
parser.add_argument("-t", "--timelines", dest="command",
                    help="Build timelines in the redis database", 
                    action='store_const',
                    const="timelines")

parser.add_argument("-l", "--list-timelines",
                    dest="command",
                    help="List current timeline",
                    action='store_const',
                    const="show")

parser.add_argument('-s', '--settings',
                    dest="command",
                    help="Generate settings file from yaml file",
                    action='store_const',
                    const="settings")

parser.add_argument('--config', required=False, help="path to config file")

parser.add_argument('-d', '--syncdb',
                    dest="command",
                    help="created database",
                    action="store_const",
                    const="db")

parser.add_argument('-u', '--usercreate',
                    dest="command",
                    help="created user",
                    action="store_const",
                    const="user")

parser.add_argument('--username', required=False, help="username")

parser.add_argument('--password', required=False, help="password")

parser.add_argument('--email', required=False, help="email")

parser.add_argument('--is_admin', required=False, help="is_admin")

parser.add_argument('-m', '--migrate',
                    dest="command",
                    help="created database",
                    action="store_const",
                    const="migrate")



parser.add_argument('--travis-config', dest="command",action="store_const", const="travis")

args = parser.parse_args()
if args.command == 'timelines':
    build_all_timelines()
elif args.command == 'show':
    showTimelines()
elif args.command == 'settings' and args.config:
    create_settings_file(args.config)
elif args.command == 'db':
    connect()
    create_tables()
elif args.command == 'usercreate' and args.username:
    create_user(args.username, args.password, args.email, args.is_admin)
elif args.command == 'travis':
    travis_setup()
elif args.command == 'migrate':
    migrate()
else:
    print("No command found")