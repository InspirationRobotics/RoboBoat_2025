#!/bin/bash

# Bash script to install Python.

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

# TODO: Everything else.