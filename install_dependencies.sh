#!/usr/bin/bash

apt-get update && apt-get install -y --no-install-recommends apt-utils
apt-get -y install curl libgomp1 libx11-dev ffmpeg libsm6 libxext6 gnupg2 liblz4-dev build-essential libroslz4-dev

pip3 install roslz4 --extra-index-url https://rospypi.github.io/simple/

pip3 install aio-pika jsondiff colorama