#!/bin/bash

cd /

echo_msg(){
    echo -e "\033[1;32m$1\033[0m"
}


echo_msg "Beginning Python installation."
sudo apt update

sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
PYTHON_VERSION=3.13
sudo apt install python${PYTHON_VERSION}
