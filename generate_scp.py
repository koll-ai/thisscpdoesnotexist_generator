import requests
import scp_gen
import time
import csv
import openai
import json


with open("./polling_api.key", "r") as f:
    NEXT_ROUND_KEY = f.read().rstrip()

# resetkey = open("reset.key", "r").read().rstrip()

url_api = "http://51.75.255.134:45900"

# Get all polls
url_poll = url_api + "/get_poll/"
r = requests.get(url_poll)
try:
    polls = r.json()['poll']
except :
    print("nothing to generate")
    next_time = str(int(time.time() + 3600))
    PARAMS = {'key': NEXT_ROUND_KEY,
              'next_time': next_time}

    r = requests.get(url=url_api + "/next_round/", params=PARAMS)

    exit(0)

# Get winner
newlist = list(reversed(sorted(polls, key=lambda k: k['votes'])))

win = newlist[0]

# set variables
object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
class_to_num = {c : i for i,c in enumerate(object_classes)}


# prepare inputs
raw_prompt = win['prompt']
prompt = raw_prompt[12:]

url_poll = url_api + "/current_scp_number/"
r = requests.get(url_poll)
scp_num = r.text

# generate scp
print("==============DEBUG=========================================")
print(scp_num)
print(prompt)
print("============================================================")

scp_gen.connect()
scp = scp_gen.generate_scp(scp_num, prompt, win['scpClass'])
print('RAW SCP :')
print(scp)
print('END raw SCP')

#with open("last_raw.txt", "w") as f:
#    f.write(scp)

# save scp
filename = 'SCP-' + scp_num + '-GPT.txt'
with open("../SCP_BDD/" + filename, 'w+') as f:
    f.write(scp)
f.close()

with open("../SCP_API/Tsde_polling_api/last.txt", 'w+') as f:
    f.write(scp)
f.close()

with open("../SCP_BDD/scp_list.csv", 'a') as f:
    writer = csv.writer(f)
    writer.writerow([scp_num, prompt, win['scpClass'], filename, win['nsfw'], win['author']])
f.close()

next_time = str(int(time.time() + 3600))
PARAMS = {'key': NEXT_ROUND_KEY,
         'next_time' : next_time}
  
r = requests.get(url = url_api + "/next_round/", params = PARAMS)

if __name__ == '__main__':
    pass
