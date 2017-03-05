#!/bin/bash
pkill -INT tee
pkill -INT raspivid
pkill -INT gst-launch-1.0

# Find an available file name
STORAGE_DIR="/home/pi/capturedVideo/"
mkdir -p $STORAGE_DIR

# Wait for the dir to be created. Also wait for the process to clean up and terminate
sleep 1

fileIndex="0"
fileName="rov_video"
extension=".h264"
fullFilePath=$STORAGE_DIR$fileName$fileIndex$extension

while [ -f $STORAGE_DIR$fileName$fileIndex$extension ]
do
	fileIndex=$[$fileIndex+1]
	fullFilePath=$STORAGE_DIR$fileName$fileIndex$extension
done
safeFileName=$fileName$fileIndex$extension

echo $safeFileName

# Start piping video into the chosen file!
#raspivid -t 0 -w 1080 -h 720 -fps 25 -hf -vf -awb off -awbg 1.9,1.6 -drc high -b 2000000 -o - | tee $STORAGE_DIR$safeFileName | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=172.28.0.12 port=5000 &

raspivid -t 0 -w 1080 -h 720 -fps 25 -hf -vf -awb cloud -drc high -b 2000000 -o - | tee $STORAGE_DIR$safeFileName | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=172.28.0.12 port=5000 &
