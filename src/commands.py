from argparse import ArgumentParser

from services.create_timelines import *
from utils.settings_creator import create_settings_file, travis_setup

from manage_db import (connect, create_tables)

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
elif args.command == 'travis':
    travis_setup()
else:
    print("No command found")