import openai
import sys
import re
import time

ERROR_UNSAFE_CONTENT = "Error: unsafe content detected"

object_classes = ['Safe', 'Euclid', 'Keter', 'Thaumiel']
username = "-1"

def connect():
    key = open("openai.key", "r").read().rstrip()
    openai.api_key = key
    print("connected to openAI")


def req_complete(prompt, max_tokens, temp=0.45, stops = ['\nItem #:', '\nDescription:', '\nAddendum', '\nRecovery:']):
    text = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=temp,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=1.0,
        presence_penalty=0.0,
        stop=stops,
        user=username
    )["choices"][0]["text"]

    return text


def remove_last_sentence(s):
    return s[::-1].split(".", 1)[1][::-1] + '.'


def generate_scp(scp_number, description, object_class):
    # get current hour from time module
    global username
    username = str(int(time.time() / 3600))

    prompt = 'SCP-' + str(scp_number) + ' is ' + description + '\n\n' \
             + 'Item #: ' + 'SCP-' + scp_number + '\n\n' \
             + 'Object Class: ' + object_class
             
    desc_field = req_complete(prompt + '\n\nDescription:', 700, stops=['\nSpecial Containment Procedures:', '\nDescription:', '\nAddendum', '\nRecovery:'])
    if getSafetyLabel(desc_field) == 2:
        return ERROR_UNSAFE_CONTENT

    proc_field = req_complete(prompt + '\n\nDescription:' + desc_field + "\n\nSpecial Containment Procedures:", 300, temp=0.3)
    if getSafetyLabel(proc_field) == 2:
        return ERROR_UNSAFE_CONTENT

    prompt += "\n\nSpecial Containment Procedures:" + proc_field
    prompt += "\n\nDescription:" + desc_field

    # prompt += "\n\nRecovery:"
    # ret = req_complete(prompt, 200, temp=0.5)
    # if getSafetyLabel(ret) == 2:
    #     return ERROR_UNSAFE_CONTENT
    # prompt += ret

    addendum0 = req_complete(prompt + "\n\nAddendum " + str(scp_number) + ".1: ", 900)
    if getSafetyLabel(addendum0) == 2:
        return ERROR_UNSAFE_CONTENT
    prompt += "\n\nAddendum " + str(scp_number) + ".1: " + addendum0

    addendum1 = req_complete(prompt + "\n\nAddendum " + str(scp_number) + ".2: Interview with ", 900)
    if getSafetyLabel(addendum1) == 2:
        return ERROR_UNSAFE_CONTENT

    addendum2 = req_complete(prompt + "\n\nAddendum " + str(scp_number) + ".3: Experiment Log :", 900)
    if getSafetyLabel(addendum2) == 2:
        return ERROR_UNSAFE_CONTENT

    prompt += "\n\nAddendum " + str(scp_number) + ".2: Interview with " + addendum1
    prompt += "\n\nAddendum " + str(scp_number) + ".3: Experiment Log :" + addendum2

    return prompt


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


def toHTML(text):
    split = text.split('\n', 1)
    text = "<center> <h3> <i>" + split[0] + "</i> </h3> </center>" + split[1]

    # entre guillemmets en italique
    text = re.sub(r'"([^"]*)"', r'<i>"\1"</i>', text)

    # termes insérés <=> toujous présents
    for s in ["Item #:", "Object Class:", "Special Containment Procedures:", "Description:", "Recovery:"]:
        text = re.sub(r"" + s, r"<h3>" + s + "</h3>", text)
    text = re.sub(r'Addendum ?(\d*)\.([^\d]*)(\d): ', r"<h3>Addendum \1.\3 : </h3>", text)

    # first line of the interview format
    text = re.sub(r'Interviewed:([^\n]*?)Interviewer:([^\n]*?)(<Begin Log>|Foreword:)', r"<b>Interviewed: \1</b> <b>Interviewer: \2</b> <br> \3", text)

    # mot avant ":" saut de ligne et en gras pendant les interviews
    text = re.sub(r'([0-9A-Za-z#\-█.\]\[]{4,}: )', r"\n\n<b>\1</b>", text)
    text = re.sub(r'(Dr.|Mr.|Mme.|Ms.) \n\n<b>([^<]+)</b>', r"\n\n<b>\2 \1</b>", text)
    text = re.sub(r'Closing \n\n<b>Statement:</b>', r"\n\n<b>\2 \1</b>", text)

    #strikethrough text when inside ~~
    text = re.sub(r"~~([^~]*)~~", r"<s>\1</s>", text)

    #block quote
    # text = re.sub(r'<Begin Log>', r"<Begin Log><blockquote class='blockquote'>", text)
    # text = re.sub(r'<End Log>', r"</blockquote><End Log>", text)

    # escape html brackets
    text = re.sub(r"<Begin Log>", r"\n\n&lt;Begin Log&gt\n\n", text)
    text = re.sub(r"<End Log>", r"\n\n&lt;End Log&gt\n\n", text)

    # nom du scp en italique
    text = re.sub(r"SCP\-([0-9]+)", r"<i>SCP-\1</i>", text)

    text = re.sub(r"\n+<([^>]*)>\n+", r"\n\n<\1>", text)
    text = re.sub(r"\n", r"<br>", text)
    text = re.sub(r"( *<br> *){3,}", r"<br><br>", text)

    text = "<div class='justifier'>" + text + "</div>"
    text = "<style>.justifier {  text-align: justify;  text-justify: inter-word;}</style>" + text

    return text
