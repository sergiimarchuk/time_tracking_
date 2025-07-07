import sys
import os

# Construct absolute path to your libs directory relative to this script or project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
libs_path = os.path.join(project_root, 'libs')

# Insert libs directory at the front of sys.path so imports find it first
sys.path.insert(0, libs_path)

# Now import pam module installed in libs
from pam import pam



from pam import pam
import sys

username = sys.argv[1]
password = sys.argv[2]

if pam().authenticate(username, password):
    print("Authentication successful")
    sys.exit(0)
else:
    print("Authentication failed")
    sys.exit(1)
