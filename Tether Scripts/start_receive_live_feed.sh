#!/bin/bash

until 1; do
   gst-launch-1.0 -v tcpclientsrc host=172.28.0.12 port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false
   echo "Restarting process in 2 seconds..."
   sleep 2
done
