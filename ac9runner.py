#! ac9runner.py

import os
import subprocess
import logging
from getpass import getpass
import unittest
from unittest.mock import patch

# Configure logging
logging.basicConfig(filename='/var/log/security_setup.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """Run a shell command and log the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e.stderr.decode()}")
        raise

def disable_root_login():
    """Disable root login via SSH."""
    logging.info("Disabling root SSH login.")
    run_command("sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config")
    run_command("systemctl restart ssh")

def create_maintenance_user():
    """Create a maintenance user with sudo access."""
    username = "maintenance"
    password = getpass("Enter a complex password for the maintenance user: ")
    
    logging.info(f"Creating maintenance user '{username}'.")
    run_command(f"useradd -m -s /bin/bash {username}")
    run_command(f"echo '{username}:{password}' | chpasswd")
    run_command(f"usermod -aG sudo {username}")

    # Change SSH port (assuming 2222 for the example)
    logging.info("Changing SSH port to 8979.")
    run_command("sed -i 's/#Port 22/Port 8979/' /etc/ssh/sshd_config")
    run_command("systemctl restart ssh")

def setup_startup_scripts():
    """Create startup scripts."""
    startup_script = """#!/bin/bash
    # Enable VPN
    your_vpn_command || { echo "VPN connection failed"; exit 1; }
    /path/to/your/automation_script.sh
    apt update && apt upgrade -y
    systemctl start your_daemon.service
    """
    
    script_path = "/etc/init.d/security_startup.sh"
    with open(script_path, 'w') as f:
        f.write(startup_script)
    
    run_command(f"chmod +x {script_path}")
    run_command(f"update-rc.d security_startup.sh defaults")

def configure_firewall():
    """Configure firewall rules."""
    logging.info("Setting up firewall rules to allow ports 8000-9000.")
    run_command("ufw default deny")
    run_command("ufw allow 8000:9000/tcp")
    run_command("ufw enable")

def enable_selinux():
    """Enable SELinux."""
    logging.info("Enabling SELinux.")
    run_command("apt install selinux -y")
    run_command("setenforce 1")

def install_chkrootkit():
    """Install chkrootkit for rootkit protection."""
    logging.info("Installing chkrootkit.")
    run_command("apt install chkrootkit -y")

def main():
    logging.info("Starting security setup script.")

    disable_root_login()
    create_maintenance_user()
    setup_startup_scripts()
    configure_firewall()
    enable_selinux()
    install_chkrootkit()

    logging.info("Security setup script completed.")

class TestSecuritySetup(unittest.TestCase):

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        mock_run.return_value.stdout = b'Success'
        mock_run.return_value.returncode = 0
        run_command('echo Hello')
        mock_run.assert_called_with('echo Hello', shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ls')
        with self.assertRaises(subprocess.CalledProcessError):
            run_command('ls non_existent_file')

    @patch('subprocess.run')
    def test_disable_root_login(self, mock_run):
        disable_root_login()
        self.assertEqual(mock_run.call_count, 2)

    @patch('subprocess.run')
    @patch('getpass.getpass', return_value='complexpassword')
    def test_create_maintenance_user(self, mock_getpass, mock_run):
        create_maintenance_user()
        self.assertEqual(mock_run.call_count, 4)

    @patch('subprocess.run')
    def test_setup_startup_scripts(self, mock_run):
        setup_startup_scripts()
        self.assertEqual(mock_run.call_count, 3)

    @patch('subprocess.run')
    def test_configure_firewall(self, mock_run):
        configure_firewall()
        self.assertEqual(mock_run.call_count, 3)

    @patch('subprocess.run')
    def test_enable_selinux(self, mock_run):
        enable_selinux()
        self.assertEqual(mock_run.call_count, 2)

    @patch('subprocess.run')
    def test_install_chkrootkit(self, mock_run):
        install_chkrootkit()
        self.assertEqual(mock_run.call_count, 2)

if __name__ == "__main__":
    if os.geteuid() != 0:
        logging.error("This script must be run as root.")
        raise SystemExit("This script must be run as root.")
    main()