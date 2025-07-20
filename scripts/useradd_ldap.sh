#!/bin/bash

# Config
UID="e220314_t1"
PASS="1qaz"
CN="$UID"
SN="314"
LDIF_FILE="user_${UID}.ldif"
MOD_FILE="mod_${UID}.ldif"

# Generate hashed password
HASHED_PASS=$(slappasswd -s $PASS)

# Create LDIF file with hashed password
cat > $LDIF_FILE <<EOF
dn: uid=$UID,ou=users,dc=myorg,dc=local
objectClass: inetOrgPerson
cn: $CN
sn: $SN
uid: $UID
userPassword: $HASHED_PASS
EOF

# Create objectClass modifier
cat > $MOD_FILE <<EOF
dn: uid=$UID,ou=users,dc=myorg,dc=local
changetype: modify
add: objectClass
objectClass: simpleSecurityObject
EOF

# Copy files into container
docker cp $LDIF_FILE openldap:/$LDIF_FILE
docker cp $MOD_FILE openldap:/$MOD_FILE

# Add user and modify objectClass
docker exec -it openldap ldapadd -x -D "cn=admin,dc=myorg,dc=local" -w admin -f /$LDIF_FILE
docker exec -it openldap ldapmodify -x -D "cn=admin,dc=myorg,dc=local" -w admin -f /$MOD_FILE

echo "[✔] User $UID created and authentication enabled."

