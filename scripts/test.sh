#!/bin/bash

read -p "Username: " USER
read -s -p "Password: " PASS
echo

if python3 auth_checker.py "$USER" "$PASS"; then
    echo "Access granted"
else
    echo "Access denied"
fi

