#!/bin/bash
# Note that this file is not useful, since git will have to be installed before this repository can be cloned.

echo "Beginning Git installation."
sudo add-apt-repository -y ppa:git-core/ppa
sudo apt update
sudo apt install -y git
echo "Git installation complete."
