import sys

import bjoern

from example import app


def run(server, port):
    print("Starting server at http://{}:{}".format(server, port))
    bjoern.run(app, server, port)


if __name__ == '__main__':


    if len(sys.argv) != 3:
        raise BaseException("Invalid number of arguments")
    
    server = sys.argv[1]
    port = int(sys.argv[2])
    
    run(server, port)
