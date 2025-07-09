import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')
from ldap3 import Server, Connection, ALL

LDAP_SERVER = 'localhost'
BASE_DN = 'ou=users,dc=myorg,dc=local'

def authenticate_and_get_info(username, password):
    user_dn = f"uid={username},{BASE_DN}"
    server = Server(LDAP_SERVER, port=389, get_info=ALL)

    try:
        # Bind using the user's credentials
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)

        # Search only in the user's own DN
        conn.search(
            search_base=user_dn,
            search_filter='(objectClass=*)',
            attributes=["cn", "mail", "entryUUID"]
        )

        if not conn.entries:
            print("[ERROR] No entries found for user.", file=sys.stderr)
            return False

        user_entry = conn.entries[0]
        return {
            "uid": username,
            "cn": user_entry.cn.value,
            "email": user_entry.mail.value if 'mail' in user_entry else None,
            "entryUUID": user_entry.entryUUID.value
        }

    except Exception as e:
        print(f"LDAP auth error: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: uid_openldap_getting.py <username> <password>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    user_info = authenticate_and_get_info(username, password)

    if user_info:
        print(user_info["uid"], user_info["cn"], user_info["email"], user_info["entryUUID"])
        sys.exit(0)
    else:
        sys.exit(1)
