#!/bin/bash
set -e
# Initialize git repo and make a clean first commit
if [ -d .git ]; then
  echo ".git already exists"
  exit 0
fi
git init
git add .
git commit -m "chore: initial SynapseFlow final v5"
# create main branch
git branch -M main
echo "Repository initialized. Now you can add remote and push."
