import serverclient
import sys
import os
import argparse

global owned
owned = []

global sign
sign = False

sys.path.append(".")
current_dir = os.getcwd()
file_dir = os.path.join(current_dir, r'share')
if not os.path.exists(file_dir):
    os.makedirs(file_dir)


parser = argparse.ArgumentParser()
parser.add_argument('-i','--ip', nargs='+', help='<Required> Set IP', required=True)
content, part = parser.parse_args()._get_kwargs()[0]
clients = part[0]
theclients = clients.split(",")

if __name__ == '__main__':
   print('STARTING=======>')
   START = serverclient.server_client(theclients)

