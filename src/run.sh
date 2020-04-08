#!/bin/bash 

# https://askubuntu.com/questions/791351/run-virtualenv-in-new-terminal-tab-automatically
# sudo apt install xclip, xdotool, wmctrl

# Copy the clipboard content to restore later
original_clipboard=$(xclip -o)

# Copy the path of your virtual environment to clipboard
echo $VIRTUAL_ENV | xclip


##################################################################
# 1) start django server
##################################################################
# The following four lines open a new tab and switch to it.
# Copied from: https://stackoverflow.com/a/2191093/10953328
WID=$(xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)"| awk '{print $5}')
xdotool windowfocus $WID
xdotool key ctrl+shift+t
wmctrl -i -a $WID

# Activate your virtualenv
xdotool type --delay 0.5 --clearmodifiers "conda $(xclip -o) activate env_face_recognition"
xdotool key Return;

# move inside image_recognition folder
xdotool type --delay 0.5 --clearmodifiers "cd ${0%/*}/image_recognition"
xdotool key Return;

# run python script
xdotool type --delay 0.5 --clearmodifiers "python manage.py runserver"
xdotool key Return;


##################################################################
# 2) Celery background process
##################################################################
# The following four lines open a new tab and switch to it.
# Copied from: https://stackoverflow.com/a/2191093/10953328
WID=$(xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)"| awk '{print $5}')
xdotool windowfocus $WID
xdotool key ctrl+shift+t
wmctrl -i -a $WID

# Activate your virtualenv
xdotool type --delay 0.5 --clearmodifiers "conda $(xclip -o) activate env_face_recognition"
xdotool key Return;

# move inside image_recognition folder
xdotool type --delay 0.9 --clearmodifiers "cd ${0%/*}/image_recognition"
xdotool key Return;

# run python script
xdotool type --delay 1.5 --clearmodifiers "celery -A image_recognition_project worker -l info -B"
xdotool key Return;


##################################################################
# 3) api face recognition
##################################################################
# The following four lines open a new tab and switch to it.
# Copied from: https://stackoverflow.com/a/2191093/10953328
WID=$(xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)"| awk '{print $5}')
xdotool windowfocus $WID
xdotool key ctrl+shift+t
wmctrl -i -a $WID

# Activate your virtualenv
xdotool type --delay 0.5 --clearmodifiers "conda $(xclip -o) activate env_face_recognition"
xdotool key Return;

# move inside api_recognition folder
xdotool type --delay 0.6 --clearmodifiers "cd ${0%/*}/recognition_api"
xdotool key Return;

# run python script
xdotool type --delay 0.9 --clearmodifiers "python views.py"
xdotool key Return;


##################################################################
# 4) start api emotion
##################################################################
# The following four lines open a new tab and switch to it.
# Copied from: https://stackoverflow.com/a/2191093/10953328
WID=$(xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)"| awk '{print $5}')
xdotool windowfocus $WID
xdotool key ctrl+shift+t
wmctrl -i -a $WID

# Activate your virtualenv
xdotool type --delay 0.8 --clearmodifiers "conda $(xclip -o) activate env_face_recognition"
xdotool key Return;

# move inside api_recognition folder
xdotool type --delay 1.1 --clearmodifiers "cd ${0%/*}/emotion_api"
xdotool key Return;

# run python script
xdotool type --delay 1.8 --clearmodifiers "python api.py"
xdotool key Return;
# Restore the original clipboard content
echo $original_clipboard | xclip
