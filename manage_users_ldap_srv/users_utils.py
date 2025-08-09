import os
import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')  # make sure this path is correct


LDIF_TEMPLATE = """dn: uid={login},ou=users,dc=myorg,dc=local
objectClass: inetOrgPerson
cn: {name}
sn: {surname}
uid: {login}
mail: {email}
userPassword: {password}
"""

OBJECTCLASS_FIX = """dn: uid={login},ou=users,dc=myorg,dc=local
changetype: modify
add: objectClass
objectClass: simpleSecurityObject
"""

def create_ldif_files(login, name, email, password):
    surname = name.split()[-1]
    user_ldif_path = f"/tmp/{login}.ldif"
    fix_ldif_path = f"/tmp/{login}_fix.ldif"

    with open(user_ldif_path, "w") as f:
        f.write(LDIF_TEMPLATE.format(
            login=login,
            name=name,
            surname=surname,
            email=email,
            password=password
        ))

    with open(fix_ldif_path, "w") as f:
        f.write(OBJECTCLASS_FIX.format(login=login))

    return user_ldif_path, fix_ldif_path

def add_user_to_ldap(login, name, email, password):
    user_ldif, fix_ldif = create_ldif_files(login, name, email, password)

    cmds = [
        f"docker cp {user_ldif} openldap:/{login}.ldif",
        f"docker exec openldap ldapadd -x -D 'cn=admin,dc=MyOrg,dc=local' -w admin -f /{login}.ldif",
        f"docker cp {fix_ldif} openldap:/{login}_fix.ldif",
        f"docker exec openldap ldapmodify -x -D 'cn=admin,dc=MyOrg,dc=local' -w admin -f /{login}_fix.ldif"
    ]

    for cmd in cmds:
        exit_code = os.system(cmd)
        if exit_code != 0:
            raise RuntimeError(f"Command failed: {cmd}")

    
    
    
import psycopg2

def insert_user_to_db(first_name, second_name, email, extra_info, ldap_entry_uuid):
    conn = psycopg2.connect(
        dbname="mydatabase",  # ✅ correct DB name from your setup
        user="myuser",
        password="mypassword",
        host="localhost",
        port="55432"
    )
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO auto_time_tracker.users (ldap_entry_uuid, vor_name, nach_name, additional_contact_info, email)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        ldap_entry_uuid,
        first_name,
        second_name,
        extra_info,
        email
    ))

    conn.commit()
    cursor.close()
    conn.close()


