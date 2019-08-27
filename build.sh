#!/usr/bin/env bash

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    EXECUTABLE_NAME="do-Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    EXECUTABLE_NAME="do-Darwin"
fi
pip3 install -r requirements.txt
pyinstaller -F --hidden-import=utils -n "$EXECUTABLE_NAME" do
