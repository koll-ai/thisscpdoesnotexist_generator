# WARNING if change on cpt, need to change time.sleep value

import time
import os
import requests

cpt = 5

with open("./polling_api.key", "r") as f:
    NEXT_ROUND_KEY = f.read().rstrip()


while True:

    print('saving data')
    requests.get("http://51.75.255.134:45900/save_data/?key=" + NEXT_ROUND_KEY)
    cpt +=1

    if cpt == 6:
        print('generating scp')
        os.system('./generator.sh')
        cpt = 0

    time.sleep(600)
    