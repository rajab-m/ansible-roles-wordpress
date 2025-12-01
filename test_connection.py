# test_remote_mysql_and_web_key.py
import pytest
import paramiko
import mysql.connector
from mysql.connector import Error
import requests

# --- IP addresses ---
WEB_SERVER_IP = "35.180.87.58"  # web server IP
DB_SERVER_IP = "172.31.37.215"   # DB server IP

# --- DNS name for HTTP check ---
WEB_SERVER_DNS = "ec2-51-44-4-181.eu-west-3.compute.amazonaws.com"

# --- SSH / Web Server Info ---
WEB_SERVER_USER = "datascientest"
WEB_SERVER_KEY_PATH = "/home/datascientest/Rajab-datascientest_keypair.pem"  # path to private key

# --- MySQL DB Info ---
DB_PORT = 3306
DB_USER = "datascientest"
DB_PASSWORD = "datascientest"
DB_NAME = "datascientest"

def test_tcp_connection_from_web_to_db():
    """
    SSH into web server and test TCP connection to DB server port 3306
    """
    remote_script = f"""
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(("{DB_SERVER_IP}", {DB_PORT}))
    print("SUCCESS")
except Exception as e:
    print("FAILURE:", e)
finally:
    s.close()
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(WEB_SERVER_KEY_PATH)
    ssh.connect(WEB_SERVER_IP, username=WEB_SERVER_USER, pkey=key)

    stdin, stdout, stderr = ssh.exec_command(f"python3 -c '{remote_script}'")
    output = stdout.read().decode().strip()
    error_output = stderr.read().decode().strip()
    ssh.close()

    print("Remote TCP test output:", output)
    if error_output:
        print("Remote TCP test errors:", error_output)

    assert "SUCCESS" in output, f"Web server cannot reach DB server on port {DB_PORT}!"

def test_local_ssh_to_web():
    """
    Test SSH connectivity from host to web server IP using private key
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        key = paramiko.RSAKey.from_private_key_file(WEB_SERVER_KEY_PATH)
        ssh.connect(WEB_SERVER_IP, username=WEB_SERVER_USER, pkey=key)

        stdin, stdout, stderr = ssh.exec_command("echo 'SSH connection successful'")
        output = stdout.read().decode().strip()
        print("SSH check output:", output)
        ssh.close()
    except Exception as e:
        pytest.fail(f"Failed to SSH into web server: {e}")

def test_local_http_to_web_dns():
    """
    Test HTTP connectivity from host to web server DNS and show content
    """
    try:
        response = requests.get(f"http://{WEB_SERVER_DNS}", timeout=5)
        print("HTTP response from web server DNS:")
        print(response.text[:500])  # show first 500 chars
        assert response.status_code == 200, "Web server returned non-200 status!"
    except requests.RequestException as e:
        pytest.fail(f"Failed to connect to web server via DNS HTTP: {e}")

def test_ssh_to_db_and_check_database_cli():
    """
    SSH into DB server and check if database 'datascientest' exists using MySQL CLI
    """

    # Command to run on DB server
    check_cmd = f"mysql -u{DB_USER} -p'{DB_PASSWORD}' -e \"SHOW DATABASES LIKE '{DB_NAME}';\""

    # SSH into the DB server
    ssh = paramiko.SSHClient()  # create SSH client
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # auto-accept host key
    key = paramiko.RSAKey.from_private_key_file(WEB_SERVER_KEY_PATH)  # your private key
    ssh.connect(DB_SERVER_IP, username=WEB_SERVER_USER, pkey=key)  # SSH connection happens here!

    # Run the command on the remote DB server
    stdin, stdout, stderr = ssh.exec_command(check_cmd)  # execute command via SSH
    output = stdout.read().decode().strip()
    error_output = stderr.read().decode().strip()

    # Close SSH connection
    ssh.close()

    # Show outputs
    print("DB CLI check output:", output)
    if error_output:
        print("DB CLI check errors:", error_output)

    # Assert the database exists
    assert DB_NAME in output, f"Database '{DB_NAME}' does not exist on DB server!"

