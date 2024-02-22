from markdown import markdown
from openai import OpenAI
import openai
import time
import sys
import re
import os


def connect():
    key = open("openai.key", "r").read().rstrip()
    os.environ["OPENAI_API_KEY"] = key
    openai.api_key = key
    print("connected to openAI")


def generate_scp(scp_num, scp_prompt, scp_class):
    client = OpenAI()

    system_prompt = f"""Create an SCP description in markdown. The description can be quite long if needed
There should be a whole narrative to the SCP using all of the Description, Special Containment Procedures, and Addenda sections to add depth to the SCP story. 
You can add some elements to the SCP story if it suit the narrative. Just be creative and make it interesting :)
The chapter titles are:
    - "###Item #: <item number> - <suspenseful title>"
    - "###Object Class:"
    - "###Description:"
    - "###Special Containment Procedures:"
    - "###Addendum 1:", "###Addendum 2:", etc. 
There are 7-10 addenda, each with a different title and content.
An addendum can contain multiple subsection to add depth and narrative value
An addendum can be one of the following types:

General Information: This type often includes supplementary information that doesn't fit into the initial description or containment procedures, such as historical background, discovery circumstances, or theoretical explanations.
Incident Reports: These addenda detail specific incidents involving the SCP, such as containment breaches, accidents during testing, or unusual activities observed. They often serve to illustrate the SCP's capabilities or the risks it poses.
Experiment Logs: This type focuses on the documentation of experiments conducted on or with the SCP. These logs can reveal the SCP's properties, effects, and potential applications or dangers.
Interview Logs: Interviews with the SCP (if it's sentient), witnesses, or individuals affected by the SCP are included here. These addenda provide personal insights and firsthand accounts that contribute to the narrative depth.
Recovery Logs: Details regarding the SCP's recovery, including the location, conditions of discovery, and any initial containment efforts, are documented here. This can also include information on any entities or organizations previously in possession of the SCP.
Updates: Sometimes, changes in containment procedures, status updates, or significant new information about the SCP are added in this form of addendum, ensuring the documentation remains current.
Miscellaneous:Any other relevant information that doesn't fit into the above categories but is deemed necessary for understanding the SCP or its containment falls here. This can include legal documents, external correspondence, or theoretical essays.

The experiment log should contain multiple expirements.
"""

    user_prompt = f"Item #{scp_num}: {scp_prompt}, class: {scp_class}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    result = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages
    )

    scp_markdown = result.choices[0].message.content
    print(scp_markdown)        

    # regex to get everything after Description et before Special Containment Procedures
    pattern = r"### Description:\n(.*?)\n### Special Containment Procedures:"
    matches = re.search(pattern, scp_markdown, re.DOTALL)
    description = matches.group(1).strip()
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Generate a picture for this SCP:\n{description}",
        size="1792x1024",
        quality="hd",
        n=1,
    )
    try:
        image_url = response.data[0].url
        print(image_url)
        pattern_to_insert_image = r"(### Object Class: .*\n)"
        scp_markdown = re.sub(pattern_to_insert_image, r"\1\n![AI SCP Image](" + image_url + ")\n", scp_markdown, count=1)
    except:
        print("No image generated")

    scp_html = markdown(scp_markdown)
    scp_html = """
    <style>
        .justifier {text-align: justify; text-justify: inter-word;}
        img{width: 100%;}
    </style>

    <div class="justifier">
    """ + f"""
    <center> <h3> SCP-{scp_num} is {scp_prompt} </h3> </center>
    """ + scp_html + "</div>"

    return scp_html
