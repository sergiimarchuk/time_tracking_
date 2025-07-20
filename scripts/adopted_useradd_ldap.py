import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')  # adjust if needed

from ldap3 import Server, Connection, ALL

# LDAP server info
LDAP_SERVER = 'ldap://localhost:389'
ADMIN_DN = 'cn=admin,dc=myorg,dc=local'
ADMIN_PASSWORD = 'admin'

# New user info
USER_UID = 'e220314_b1'
USER_CN = 'e220314_b1'  # common name, can be full name or username
USER_GIVENNAME = 'Sergii'  # example first name
USER_SN = 'Ivanov'         # example surname
USER_EMAIL = 'sergii@example.com'
USER_PASSWORD = '1qaz1'
USER_DN = f'uid={USER_UID},ou=users,dc=myorg,dc=local'

server = Server(LDAP_SERVER, get_info=ALL)
conn = Connection(server, ADMIN_DN, ADMIN_PASSWORD, auto_bind=True)

# Create user entry with extra attributes
entry = {
    'objectClass': ['inetOrgPerson', 'simpleSecurityObject'],
    'cn': USER_CN,
    'givenName': USER_GIVENNAME,
    'sn': USER_SN,
    'uid': USER_UID,
    'mail': USER_EMAIL,
    'userPassword': USER_PASSWORD,
}

if conn.add(USER_DN, attributes=entry):
    print(f"[✔] User {USER_UID} created.")
else:
    print(f"[✘] Failed to create user: {conn.result['description']}")

conn.unbind()

