from markdown import markdown
from openai import OpenAI
import openai
import time
import sys
import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER")
API_URL = os.getenv("API_URL")

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
An addendum can contain multiple subsection to add depth and narrative value
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
        prompt=f"Generate a picture for this SCP:\n{description}", #TODO better prompt engineering for this part
        size="1792x1024",
        quality="hd",
        n=1,
    )

    image_tag = ""

    try:
        image_url = response.data[0].url

        save_url = f"{IMAGE_FOLDER}/SCP-{scp_num}-GPT.png"
        api_url = f"{API_URL}/images/SCP-{scp_num}-GPT.png"
        
        response= requests.get(image_url)
        if response.status_code == 200:
            with open(save_url, 'wb') as file:
                file.write(response.content)

        image_tag = f"""
            <img class="scp-image" src="{api_url}" alt="Illustration of SCP-{scp_num}" />
        """
    except:
        image_tag = f"""
            <img class="scp-image" src="{api_url}" alt="Illustration of SCP-{scp_num}" />
        """

    scp_html = markdown(scp_markdown)
    scp_html = re.sub(r"(<h3>Object Class: .*</h3>)", image_tag, scp_html, count=1)
    
    return f"""
    <div class="justifytext">

    <center> <h3> SCP-{scp_num} is {scp_prompt} </h3> </center>

    {scp_html}

    </div>
    """
