#!/usr/bin/env bash

python3 generate_scp.py
git add raw_scp/*
git commit -m "added new SCP-GPT"
git pull
git push