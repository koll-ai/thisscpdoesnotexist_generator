import requests
import scp_gen
import time
import csv
import openai
import json

with open("/home/thisscpdoesnotexist/tsde/polling_api.key", "r") as f:
    NEXT_ROUND_KEY = f.read().rstrip()

# resetkey = open("reset.key", "r").read().rstrip()


# Get all polls
url_poll = "https://thisscpdoesnotexist.pythonanywhere.com/get_poll/"
r = requests.get(url_poll)
polls = r.json()['poll']


if len(polls) == 0:
    print("nothing to generate")
    next_time = str(int(time.time() + 3600))
    PARAMS = {'key': resetkey,
              'next_time': next_time}

    r = requests.get(url="http://thisscpdoesnotexist.pythonanywhere.com/next_round/", params=PARAMS)

    exit(0)

# Get winner
newlist = list(reversed(sorted(polls, key=lambda k: k['votes'])))



win = newlist[0]

# set variables
object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
class_to_num = {c : i for i,c in enumerate(object_classes)}


# prepare inputs
raw_prompt = win['prompt']
prompt = raw_prompt[raw_prompt.index('GPT') + 7:]

url_poll = "https://thisscpdoesnotexist.pythonanywhere.com/current_scp_number/"
r = requests.get(url_poll)
scp_num = r.text

# generate scp
print("==============DEBUG=========================================")
print(scp_num)
print(prompt)
print("============================================================")

scp_gen.connect()
scp = scp_gen.generate_scp(scp_num, prompt, win['scpClass'])
scp = scp_gen.toHTML(scp)

# save scp
filename = 'SCP-' + scp_num + '-GPT.txt'
with open("../SCP-GPT_db/" + filename, 'w+') as f:
    f.write(scp)
f.close()

with open("../tsde/last.txt", 'w+') as f:
    f.write(scp)
f.close()

with open("../SCP-GPT_db/scp_list.csv", 'a') as f:
    writer = csv.writer(f)
    writer.writerow([raw_prompt, win['scpClass'], filename])
f.close()

next_time = str(int(time.time() + 3600))
PARAMS = {'key': NEXT_ROUND_KEY,
         'next_time' : next_time}
  
r = requests.get(url = "http://thisscpdoesnotexist.pythonanywhere.com/next_round/", params = PARAMS)

if __name__ == '__main__':
    pass
