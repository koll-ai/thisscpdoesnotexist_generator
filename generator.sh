#!/usr/bin/env bash

python3 generate_scp.py

cd $HOME/SCP-GPT_db/

git add *
git commit -m "added new SCP-GPT"
git pull
git push

cd $HOME/tsde/
git add last.txt
git pull
git push