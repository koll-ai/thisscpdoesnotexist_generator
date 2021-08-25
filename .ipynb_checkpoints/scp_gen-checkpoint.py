#example :
# $python scp_gen.py  "001" "a pink burger that turns people into vegans" "0"

import openai
import sys

if len(sys.argv) != 4:
    print("You must pass a prompt and an object class")
    exit()
    
scp_number = sys.argv[1]
description = sys.argv[2]
object_class = int(sys.argv[3])

object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
stops = ['\nItem #:', '\nDescription:', '\nAddendum', '\nRecovery:']

openai.api_key = open("openai.key", "r").read()

def req_complete(prompt, max_tokens):
    return openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      temperature=0.7,
      max_tokens=max_tokens,
      top_p=1.0,
      frequency_penalty=1.0,
      presence_penalty=0.0,
      stop=stops
    )["choices"][0]["text"]

def remove_last_sentence(s):
    return s[::-1].split(".", 1)[1][::-1]+'.'

prompt = 'SCP-' + scp_number + '-GPT is ' + description + '.\n\n' \
    + 'Item #:' + 'SCP-' + scp_number + '-GPT\n\n' \
    + 'Object Class: ' + object_classes[object_class] + '\n\n' \
    + 'Special Containment Procedures:'

print("Special Containment Procedures done")
ret = req_complete(prompt, 100)
ret = remove_last_sentence(ret) #removes last uncompleted sentence
prompt += ret + "\n\nDescription:"

print("Description done")
ret = req_complete(prompt, 600)
ret = remove_last_sentence(ret) #removes last uncompleted sentence
prompt += ret + "\n\nDiscovery:"

print("Discovery done")
ret = req_complete(prompt, 600)
ret = remove_last_sentence(ret) #removes last uncompleted sentence
prompt += ret + "\n\nRecovery:"

print("Recovery done")
ret = req_complete(prompt, 600)
ret = remove_last_sentence(ret) #removes last uncompleted sentence
prompt += ret + "\n\nAddendum:"

print("Addendum done")

print(prompt)