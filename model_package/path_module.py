import os
d = os.path.dirname(__file__)

# First get the path of the current file then using os.path.dirname() get the path of the directory where the file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Get base directory of main files
BASE_DIR_MAIN = os.path.dirname(BASE_DIR)


# Create different paths to the files used in the program
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.ini')
LOG_FILE_PATH = os.path.join(BASE_DIR, 'log.log')
RSS_LOG_FILE_PATH = os.path.join(BASE_DIR, 'latest_entries.txt')
REQUIREMENTS_FILE_PATH = os.path.join(BASE_DIR_MAIN, "requirements.txt")
print(BASE_DIR_MAIN)
print(REQUIREMENTS_FILE_PATH)

# Testing purposes
if __name__ == "__main__":
    pass
