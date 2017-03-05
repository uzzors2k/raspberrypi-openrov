#!/bin/bash
pkill -INT tee
pkill -INT raspivid
pkill -INT gst-launch-1.0

# Wait for the process to clean up and terminate
sleep 1

# Auto white balance is disabled to prevent fluctuating colors
# Gains set manually here in -awgb as red gain and blue gain,
# so the first parameter after -awbg is red, the second is blue
# Green is always treated as being at x1.0
# adjusted for best white balance underwater

#raspivid -t 0 -w 1080 -h 720 -fps 25 -hf -vf -awb off -awbg 1.9,1.6 -drc high -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=172.28.0.12 port=5000 &

raspivid -t 0 -w 1080 -h 720 -fps 25 -hf -vf -awb cloud -drc high -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=172.28.0.12 port=5000 &
