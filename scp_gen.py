import openai
import sys
import re

object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
stops = ['\nItem #:', '\nDescription:', '\nAddendum', '\nRecovery:']

def connect():
    key = open("openai.key", "r").read()
    print(key)
    openai.api_key = key
    print("connected to openAI")

def req_complete(prompt, max_tokens):
    text = openai.Completion.create(
    engine="davinci",
    prompt=prompt,
    temperature=0.7,
    max_tokens=max_tokens,
    top_p=1.0,
    frequency_penalty=1.0,
    presence_penalty=0.0,
    stop=stops
    )["choices"][0]["text"]

    return remove_last_sentence(text)

def remove_last_sentence(s):
    return s[::-1].split(".", 1)[1][::-1]+'.'

def generate_scp(scp_number, description, object_class):
    prompt = 'SCP-' + str(scp_number) + '-GPT is ' + description + '.\n\n' \
        + 'Item #:' + 'SCP-' + scp_number + '-GPT\n\n' \
        + 'Object Class: ' + object_class + '\n\n' \
        + 'Special Containment Procedures:'

    ret = req_complete(prompt, 100)
    prompt += ret + "\n\nDescription:"

    ret = req_complete(prompt, 600)
    prompt += ret + "\n\nDiscovery:"

    ret = req_complete(prompt, 600)
    prompt += ret + "\n\nRecovery:"

    ret = req_complete(prompt, 600)
    prompt += ret + "\n\nAddendum 1:"

    ret = req_complete(prompt, 600)

    return prompt

def toHTML(text):
    text = re.sub(r"^(.*):",r"<h3>\1:</h3>",text)
    text = re.sub(r"\n\n(.*):",r"\n\n<h3>\1:</h3>",text)
    text = re.sub(r"SCP\-([0-9]*)\-GPT", r"<i>SCP-\1-GPT</i>", text)

    text = "<div class='justifier'>" + text + "</div>"
    text = "<style>.justifier {  text-align: justify;  text-justify: inter-word;}</style>" + text
    return text