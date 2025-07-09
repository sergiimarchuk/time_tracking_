import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')  # make sure this path is correct

from ldap3 import Server, Connection, ALL

def authenticate(username, password):
    server = Server('localhost', port=389, get_info=ALL)
    user_dn = f"uid={username},ou=users,dc=myorg,dc=local"
    try:
        conn = Connection(server, user=user_dn, password=password)
        if not conn.bind():
            print(f"Bind failed: {conn.last_error}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"LDAP authentication error: {e}", file=sys.stderr)
        return False



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: auth_checker.py <username> <password>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    if authenticate(username, password):
        sys.exit(0)
    else:
        sys.exit(1)

