import sys
import bjoern

from main import app

def start(server, port):
    print("Starting server at http://{}:{}".format(server, port))
    bjoern.run(app, server, port)

    
if __name__ == '__main__':
    
    server = sys.argv[1]
    port = int(sys.argv[2])
    start(server, port)
    
