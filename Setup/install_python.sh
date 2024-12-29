#!/bin/bash

# Bash script to install Python.
# Not tested yet.

# Function to print in bold green text.
echo_msg(){
    echo -e "\033[1;32m$1\033[0m"
}

# Check if the user has sudo privileges.
if [[$EUID -ne 0]]; then
    echo "This script must be run as root. Use sudo".
    exit 
fi 

# Function to check if a command exists.
command_exists(){
    command -v "$1" > /dev/null 2>&1
}

# Update package list.
echo_msg "Updating package list..."
apt-get update -y || (yum check-update && yum -y update)

# Install dependencies.
if command_exists apt-get; then
    apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev wget

elif command_exists yum; then
    yum groupinstall -y "Development Tools"
    yum install -y gcc zlib-devel bzip2 bzip2-devel readline-devel \
        sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel wget

else
    echo "Unsupported package manager. Please make sure you are using a Debian-based or Red Hat-based system." 
    exit 1
fi

read -p "Enter the Python version to install (e.g. 3.11.6): " PYTHON_VERSION

if command_exists python3 && [["$(python3 --version)" == *"$PYTHON_VERSION"]]; then
    echo_msg "Python $PYTHON_VERSION is already installed."
    exit 0
fi

# Download and install Python
echo_msg "Downloading Python $PYTHON_VERSION..."
wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz -0 /tmp/Python-$PYTHON_VERSION.tgz

echo "Extracting Python $PYTHON_VERSION..."
cd /tmp && tar -xzf Python-$PYTHON_VERSION.tgz

cd Python-$PYTHON_VERSION
echo "Configuring Python $PYTHON_VERSION..."

./configure --enable-optimizations

echo_msg "Building and installing $PYTHON_VERSION (this may take a while, please be patient)..."
make -j$(nproc)
make altinstall

# Verify installation
if command_exists python3.$(echo $PYTHON_VERSION | cut -d. -f2); then
    echo_msg "Python $PYTHON_VERSION installed successfully."
    python3.$(echo $PYTHON_VERSION | cut -d. -f2) --version
else
    echo_msg "Python installation failed."
    exit 1
fi

# Cleaning up
echo "Cleaning up..."
cd /tmp && rm -rf Python-$PYTHON_VERSION.tgz Python-$PYTHON_VERSION

echo_msg "Python $PYTHON_VERSION installation is complete."

