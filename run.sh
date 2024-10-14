#!/bin/bash

set -e

# Define log file
LOG_FILE="/var/log/ac9runner_install.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if user has root privileges
if [ "$(id -u)" != "0" ]; then
    log "This script must be run as root."
    echo "This script must be run as root."
    exit 1
fi

log "Starting installation."

apt update >> "$LOG_FILE" 2>&1

# Check for curl and install if not present
if ! [ -x "$(command -v curl)" ]; then
    log "Installing curl."
    apt install curl -y >> "$LOG_FILE" 2>&1
else
    log "Curl is already installed."
fi

# Check for openssl and install if not present
if ! [ -x "$(command -v openssl)" ]; then
    log "Installing openssl."
    apt install openssl -y >> "$LOG_FILE" 2>&1
else
    log "OpenSSL is already installed."
fi

# # Creating the directory where the script will be stored
# mkdir -p /etc/ac9runner
# log "Created directory /etc/ac9runner."

# # Copy the script to the /etc directory
# cp -r . /etc/ac9runner/
# log "Copied script files to /etc/ac9runner."

# Create symbolic link
ln -s /etc/ac9runner/dist/run-py /usr/bin/ac9runner
chmod +x /usr/bin/ac9runner
log "Created symbolic link /usr/bin/ac9runner."

current_minute=$(date +"%M")

# Create a cron job that runs the script every three hours
echo "$current_minute */3 * * * root /usr/bin/ac9runner" >> /etc/crontab
log "Added cron job to /etc/crontab to run ac9runner every three hours."

log "Installation completed successfully."