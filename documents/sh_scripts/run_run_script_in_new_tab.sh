#!/bin/bash 

# https://askubuntu.com/questions/791351/run-virtualenv-in-new-terminal-tab-automatically
# sudo apt install xclip, xdotool, wmctrl

# Copy the clipboard content to restore later
original_clipboard=$(xclip -o)

# Copy the path of your virtual environment to clipboard
echo $VIRTUAL_ENV | xclip


# The following four lines open a new tab and switch to it.
# Copied from: https://stackoverflow.com/a/2191093/10953328
WID=$(xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)"| awk '{print $5}')
xdotool windowfocus $WID
xdotool key ctrl+shift+t
wmctrl -i -a $WID

# Activate your virtualenv
xdotool type --delay 0.5 --clearmodifiers "source $(xclip -o) activate env_face_recognition"
xdotool key Return;

# move inside api_recognition folder
xdotool type --delay 0.5 --clearmodifiers "cd ${0%/*}/recognition_api"
xdotool key Return;

# run python script
xdotool type --delay 0.5 --clearmodifiers "python simple_request.py"
xdotool key Return;

# Restore the original clipboard content
echo $original_clipboard | xclip
