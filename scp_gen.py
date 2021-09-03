import openai
import sys
import re

object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
stops = ['\nItem #:', '\nDescription:', '\nAddendum', '\nRecovery:']

def connect():
    key = open("openai.key", "r").read().rstrip()
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
    if s[-1] != "." :
        return s[::-1].split(".", 1)[1][::-1]+'.'
    else:
        return s

def generate_scp(scp_number, description, object_class):
    prompt = 'SCP-' + str(scp_number) + '-GPT is ' + description + '.\n\n' \
        + 'Item #: ' + 'SCP-' + scp_number + '-GPT\n\n' \
        + 'Object Class: ' + object_class + '\n\n' \
        + 'Special Containment Procedures: '
    ret = req_complete(prompt, 300)

    prompt += ret + "\n\nDescription:"
    ret = req_complete(prompt, 500)

    prompt += ret + "\n\nRecovery:"
    ret = req_complete(prompt, 200)

    prompt += ret + "\n\nAddendum " + str(scp_number) +".1:"
    ret = req_complete(prompt, 600)

    prompt += ret + "\n\nAddendum " + str(scp_number) +".2:"
    ret = req_complete(prompt, 300)

    prompt += ret

    return prompt

def toHTML(text):
    split = text.split('\n',1)
    text = "<center> <h3> <i>" + split[0] +"</i> </h3> </center>"+ split[1]

    #nom du scp en italique
    text = re.sub(r"SCP\-([0-9]*)\-GPT", r"<i>SCP-\1-GPT</i>", text)
    text = re.sub(r"SCP\-([0-9]*)", r"<i>SCP-\1</i>", text)

    #entre guillemmets en italique
    text = re.sub(r'"([^"]*)"', r'<i>"\1"</i>', text)

    #mot avant ":" en gras
    text = re.sub(r'([0-9A-Za-z^:^ ]*:)', r"<b><br>\1</b>", text)

    #termes insérés <=> toujous présents
    for s in ["Item #:", "Object Class:", "Special Containment Procedures:", "Description:", "Recovery:"]:
        text = re.sub(r"" + s,r"<h3>" + s +"</h3>",text)
        
    text = re.sub(r'Addendum ?(\d*)\.([^\d]*)(\d):',r"<h3>Addendum \1.\3 :</h3>",text)

    text = re.sub("\n", "<br>", text)

    text = re.sub(r"(<br>){2,}", "<br>", text)

    text = "<div class='justifier'>" + text + "</div>"
    text = "<style>.justifier {  text-align: justify;  text-justify: inter-word;}</style>" + text
    
    return text