import paramiko
import os
from datetime import datetime, timedelta
import json
import time
import glob

def create_backup_directory():
    """Create backup directories if they don't exist"""
    backup_dirs = {
        'binary': "mikrotik_backups/binary",
        'plaintext': "mikrotik_backups/plaintext"
    }
    for dir_path in backup_dirs.values():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    return backup_dirs

def cleanup_old_backups(backup_dirs, backup_age):
    """Remove backups older than backup_age days"""
    current_time = datetime.now()
    deleted_files = []

    for backup_type, backup_dir in backup_dirs.items():
        # Get all backup files in the directory
        file_pattern = "*.backup" if backup_type == 'binary' else "*.rsc"
        backup_files = glob.glob(os.path.join(backup_dir, file_pattern))

        for backup_file in backup_files:
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
            age = current_time - file_modified_time

            if age.days > backup_age:
                try:
                    os.remove(backup_file)
                    deleted_files.append(backup_file)
                except Exception as e:
                    print(f"Error deleting old backup {backup_file}: {str(e)}")

    if deleted_files:
        print("\nCleaned up old backups:")
        for file in deleted_files:
            print(f"- Removed: {file}")
    else:
        print("\nNo old backups needed cleaning up")

def connect_to_router(router):
    """Establish an SSH connection to the router"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=router["host"],
            username=router["username"],
            password=router["password"],
            port=router.get("port", 22)
        )
        return ssh
    except Exception as e:
        print(f"Error connecting to {router['host']}: {str(e)}")
        return None

def execute_command(ssh, command):
    """Execute a command on the router via SSH"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")

def create_binary_backup(router, ssh, backup_dir):
    """Create and download a binary backup from the router"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{router['host']}_backup_{timestamp}"
        remote_backup_path = f"{backup_name}.backup"

        # Create binary backup
        command = f"/system backup save name={backup_name}"
        stdout, stderr = execute_command(ssh, command)
        if stderr:
            print(f"Error creating binary backup on {router['host']}: {stderr}")
            return None

        # Wait for the backup file to be created
        time.sleep(2)

        # Download the backup file using SFTP
        sftp = ssh.open_sftp()
        local_backup_path = os.path.join(backup_dir, remote_backup_path)
        sftp.get(remote_backup_path, local_backup_path)

        # Clean up the remote backup file
        execute_command(ssh, f"/file remove {remote_backup_path}")

        print(f"Binary backup downloaded: {local_backup_path}")
        return local_backup_path
    except Exception as e:
        print(f"Error with binary backup from {router['host']}: {str(e)}")
        return None

def create_plaintext_backup(router, ssh, backup_dir):
    """Create and download a plaintext configuration backup from the router"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{router['host']}_config_{timestamp}"
        remote_backup_path = f"{backup_name}.rsc"

        # Export the configuration
        command = f"/export file={backup_name}"
        stdout, stderr = execute_command(ssh, command)
        if stderr:
            print(f"Error creating plaintext backup on {router['host']}: {stderr}")
            return None

        # Wait for the export file to be created
        time.sleep(2)

        # Download the exported configuration file using SFTP
        sftp = ssh.open_sftp()
        local_backup_path = os.path.join(backup_dir, remote_backup_path)
        sftp.get(f"{backup_name}.rsc", local_backup_path)

        # Clean up the remote export file
        execute_command(ssh, f"/file remove {backup_name}.rsc")

        print(f"Plaintext backup downloaded: {local_backup_path}")
        return local_backup_path
    except Exception as e:
        print(f"Error with plaintext backup from {router['host']}: {str(e)}")
        return None

def main():
    # Read the configuration from JSON file
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("config.json file not found!")
        return

    # Extract routers and backup age from config
    routers = config.get("routers", [])
    backup_age = config.get("backup_age", 30)  # Default to 30 days if not specified

    if not routers:
        print("No routers found in config!")
        return

    # Create backup directories
    backup_dirs = create_backup_directory()

    # Process each router
    for router in routers:
        print(f"\nProcessing router: {router['host']}")

        # Connect to the router
        ssh = connect_to_router(router)
        if not ssh:
            print(f"Failed to connect to router: {router['host']}")
            continue

        try:
            # Create both types of backups
            print("Creating binary backup...")
            create_binary_backup(router, ssh, backup_dirs['binary'])

            print("Creating plaintext backup...")
            create_plaintext_backup(router, ssh, backup_dirs['plaintext'])

        except Exception as e:
            print(f"Error processing router {router['host']}: {str(e)}")

        finally:
            # Close the SSH connection
            ssh.close()

    # Clean up old backups
    print("\nChecking for old backups...")
    cleanup_old_backups(backup_dirs, backup_age)

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
print("\nFiles created/modified:")
print("mikrotik_backups/binary/[hostname]_backup_[timestamp].backup")
print("mikrotik_backups/plaintext/[hostname]_config_[timestamp].rsc")