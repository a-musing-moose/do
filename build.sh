#!/usr/bin/env bash
pip3 install -r requirements.txt
pyinstaller -F -n "do" --hidden-import=do.utils entrypoint.py
