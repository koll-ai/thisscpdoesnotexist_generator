#!/usr/bin/env bash

python3 generate_scp.py

cd $HOME/SCP_BDD/

git add *
git commit -m "added new SCP-GPT"
git pull
git push

cd $HOME/SCP_API/
git add last.txt
git commit -m "update last SCP"
git pull
git push