import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')  # make sure this path is correct


from ldap3 import Server, Connection, ALL, MODIFY_ADD

# LDAP server info
LDAP_SERVER = 'ldap://localhost:389'
ADMIN_DN = 'cn=admin,dc=myorg,dc=local'
ADMIN_PASSWORD = 'admin'

# New user info
USER_UID = 'e220314_b1'
USER_CN = 'e220314_b1'
USER_SN = '314'
USER_PASSWORD = '1qaz1'
USER_DN = f'uid={USER_UID},ou=users,dc=myorg,dc=local'

server = Server(LDAP_SERVER, get_info=ALL)
conn = Connection(server, ADMIN_DN, ADMIN_PASSWORD, auto_bind=True)

# Create user entry
entry = {
    'objectClass': ['inetOrgPerson', 'simpleSecurityObject'],
    'cn': USER_CN,
    'sn': USER_SN,
    'uid': USER_UID,
    'userPassword': USER_PASSWORD,
}

if conn.add(USER_DN, attributes=entry):
    print(f"[✔] User {USER_UID} created.")
else:
    print(f"[✘] Failed to create user: {conn.result['description']}")

conn.unbind()

