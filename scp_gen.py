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
    The chapters are:
        - Item #
        - Object Class
        - Description
        - Special Containment Procedures
        - three Addendums including one interview and one experiment"""

    user_prompt = f"Item #{scp_num}: {scp_prompt}, class: {scp_class}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    result = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    scp_markdown = result.choices[0].message.content

    print(scp_markdown)

    scp_html = markdown(scp_markdown)

    return scp_html
