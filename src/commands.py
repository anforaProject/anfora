from argparse import ArgumentParser

from services.create_timelines import *

parser = ArgumentParser()
parser.add_argument("-t", "--timelines", dest="command",
                    help="Build timelines in the redis database", action='store_const',const="timelines")
parser.add_argument("-l", "--list-timelines",
                    dest="command",
                    help="List current timeline",action='store_const',const="show")

args = parser.parse_args()

if args.command == 'timelines':
    build_all_timelines()
elif args.command == 'show':
    showTimelines()
