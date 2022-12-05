import openai
import sys
import re
import time

ERROR_UNSAFE_CONTENT = "Error: unsafe content detected"

class NSFWContentException(Exception):
    pass

object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
username = "-1"

def connect():
    key = open("openai.key", "r").read().rstrip()
    openai.api_key = key
    print("connected to openAI")


def req_complete(prompt, max_tokens, temp=0.45, stops = ['\nItem #:', '\nAddendum']):
    try:
        text = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=1.0,
            presence_penalty=0.45,
            stop=stops,
            user=username
        )["choices"][0]["text"]
    except openai.error.InvalidRequestError as e:
        print(e)
        text = ""

    if getSafetyLabel(text) == 2:
        raise Exception('nsfw content')

    return text


def remove_last_sentence(s):
    return s[::-1].split(".", 1)[1][::-1] + '.'


def generate_scp(scp_number, description, object_class):
    try:
        # get current hour from time module
        global username
        username = str(int(time.time() / 3600))

        scp = {}
        
        scp["prompt"] = 'SCP-' + str(scp_number) + ' is ' + description
        
        scp['item_n'] = str(scp_number)

        scp['class'] = object_class

        start_input = scp['prompt'] \
        + '\n\nItem #: SCP-' + scp['item_n'] \
        + '\n\nObject Class: ' + scp['class']

        input = start_input + '\n\nDescription:'
        scp['description'] = req_complete(input, 900, stops=['\nSpecial Containment Procedures:', '\nAddendum', '\nDescription:', '\nItem #:'])

        input = start_input + '\n\n' + 'Description:' + scp['description'] + '\n\n' + 'Special Containment Procedures:'
        scp['procedures'] = req_complete(input, 150, temp=0.3, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])

        input = start_input \
        + '\n\nSpecial Containment Procedures:' + scp['procedures'] \
        + '\n\nDescription:' + scp['description'] \
        + "\n\nAddendum " + str(scp_number) + ".1:"
        scp['addendum0'] = req_complete(input, 900, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])
        
        input = start_input \
        + '\n\nSpecial Containment Procedures:' + scp['procedures'] \
        + '\n\nDescription:' + scp['description'] \
        + "\n\nAddendum " + str(scp_number) + ".2: Interview with"
        scp['addendum1'] = req_complete(input, 150, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])
        scp['addendum1'] += req_complete(input + scp['addendum1'], 150, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])
        scp['addendum1'] += req_complete(input + scp['addendum1'], 150, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])
        scp['addendum1'] += req_complete(input + scp['addendum1'], 150, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])
        scp['addendum1'] += req_complete(input + scp['addendum1'], 150, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])

        input = start_input \
        + '\n\nSpecial Containment Procedures:' + scp['procedures'] \
        + '\n\nDescription:' + scp['description'] \
        + "\n\nAddendum " + str(scp_number) + ".3: Experiment Log"
        scp['addendum2'] = req_complete(input, 900, stops=['Click here', '\nItem #:', '\nAddendum', '\nDescription:'])

        return scp

    except NSFWContentException:
        return ERROR_UNSAFE_CONTENT


def getSafetyLabel(text):
    content_to_classify = text

    response = openai.Completion.create(
        engine="content-filter-alpha",
        prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=10,
        user=username
    )

    output_label = response["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

    # if the most probable token is none of "0", "1", or "2"
    # this should be set as unsafe
    if output_label not in ["0", "1", "2"]:
        output_label = "2"

    return output_label


def toHTML(scp):
    htmlscp = {}

    for k in scp.keys():
        htmlscp[k] = global_formating(scp[k])

    htmlscp['prompt'] = "<center> <h3> <i>" + scp['prompt'] + "</i> </h3> </center>"

    htmlscp['addendum0'] = addendum_formating(htmlscp['addendum0'])
    htmlscp['addendum1'] = interview_formating(htmlscp['addendum1'])
    htmlscp['addendum2'] = addendum_formating(htmlscp['addendum2'])

    text = "<div class='justifier'>" \
    + htmlscp['prompt'] \
    + "<h3> Item #: </h3> SCP-" + scp['item_n'] \
    + "<h3> Object Class: </h3>" + scp['class'] \
    + "<h3> Description: </h3>" + htmlscp['description'] \
    + "<h3> Special Containment Procedures: </h3>" + htmlscp['procedures'] \
    + "<h3> Addendum " + scp['item_n'] + ".1: </h3>" + htmlscp['addendum0'] \
    + "<h3> Addendum " + scp['item_n'] + ".2: </h3> Interview with" + htmlscp['addendum1'] \
    + "<h3> Addendum " + scp['item_n'] + ".3: </h3> Experiment Log" + htmlscp['addendum2'] \
    + "</div>"

    text = "<style>.justifier {  text-align: justify;  text-justify: inter-word;}</style>" + text

    return text

def global_formating(text):
    #brackets to html
    text = re.sub(r'<', r'&lt', text)
    text = re.sub(r'>', r'&gt', text)

    # entre guillemmets en italique
    text = re.sub(r'"([^"]*)"', r'<i>"\1"</i>', text)
    text = re.sub(r'\s:', r':', text)
    
    #strikethrough text when inside ~~
    text = re.sub(r"~~([^~]*)~~", r"<s>\1</s>", text)

    # nom du scp en italique
    text = re.sub(r"SCP\-([0-9]+)", r"<i>SCP-\1</i>", text)

    text = re.sub(r"\n", r"<br>", text)
    text = re.sub(r"( *<br> *){3,}", r"<br><br>", text)

    # names before : will be bold and on a new line
    text = re.sub(r'<br>([^:]{,30}:)', r"<br><b>\1</b>", text)

    return text

def interview_formating(text):
    text = re.sub(r'Interviewed:([^\n]*?)Interviewer:([^\n]*?)(<Begin Log>|Foreword:)', r"<b>Interviewed: \1</b> <b>Interviewer: \2</b> <br> \3", text)
    return text

def addendum_formating(text):
    # escape html brackets
    text = re.sub(r"<Begin Log>", r"\n\n&lt;Begin Log&gt\n\n", text)
    text = re.sub(r"<End Log>", r"\n\n&lt;End Log&gt\n\n", text)

    return text
