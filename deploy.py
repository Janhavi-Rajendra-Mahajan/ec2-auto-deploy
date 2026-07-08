import os
import paramiko

# Read GitHub Secrets
HOST = os.environ["EC2_HOST"]
USERNAME = os.environ["EC2_USERNAME"]
PRIVATE_KEY = os.environ["EC2_PRIVATE_KEY"]

KEY_FILE = "ec2_key.pem"

# Save the private key to a temporary file
with open(KEY_FILE, "w") as f:
    f.write(PRIVATE_KEY)

os.chmod(KEY_FILE, 0o600)

# Load the SSH key
try:
    key = paramiko.Ed25519Key.from_private_key_file(KEY_FILE)
except Exception:
    try:
        key = paramiko.RSAKey.from_private_key_file(KEY_FILE)
    except Exception as e:
        print("Failed to load private key:", e)
        raise

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("Connecting to EC2...")

ssh.connect(
    hostname=HOST,
    username=USERNAME,
    pkey=key,
    timeout=30
)

print("Connected successfully.")

# Upload website file
print("Uploading index.html...")

sftp = ssh.open_sftp()

sftp.put("index.html", "/tmp/index.html")

sftp.close()

print("File uploaded successfully.")

# Move file to Apache directory and restart Apache
commands = [
    "sudo mv /tmp/index.html /var/www/html/index.html",
    "sudo systemctl restart apache2"
]

for command in commands:
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)

    output = stdout.read().decode()
    error = stderr.read().decode()

    if output:
        print(output)

    if error:
        print(error)

ssh.close()

print("Website deployed successfully!")
