import subprocess
import logging

# Configure logging
logging.basicConfig(filename='git_update_check.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """Run a shell command and log the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(result.stdout.decode().strip())
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e.stderr.decode().strip()}")
        return None

def check_current_branch():
    """Check the current Git branch."""
    branch = run_command("git rev-parse --abbrev-ref HEAD")
    return branch

def checkout_main():
    """Checkout to the main branch."""
    logging.info("Checking out to the main branch.")
    run_command("git checkout main")

def pull_latest():
    """Pull the latest changes from the origin main."""
    logging.info("Pulling latest changes from origin main.")
    run_command("git pull origin main")

def check_diff():
    """Check for differences after the pull."""
    diff = run_command("git diff")
    if diff:
        logging.info("Changes detected:")
        logging.info(diff)
    else:
        logging.info("No changes detected.")

def main():
    logging.info("Starting git update check.")
    
    current_branch = check_current_branch()
    logging.info(f"Current branch: {current_branch}")

    if current_branch != "main":
        checkout_main()

    pull_latest()
    check_diff()
    
    logging.info("Git update check completed.")

if __name__ == "__main__":
    main()
