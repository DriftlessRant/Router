# MikroTik Router Backup Tool

A Python script for automated backup of MikroTik routers, creating both binary (.backup) and plaintext configuration (.rsc) backups with automatic cleanup of old backup files.

## Features

- Creates both binary and plaintext configuration backups
- Supports multiple routers
- Automatic cleanup of old backup files
- Organized backup directory structure
- Secure SSH connection handling
- Automatic remote file cleanup after download
- Configurable backup retention period

## Prerequisites

- Python 3.6 or higher
- MikroTik router(s) with SSH access enabled
- Network connectivity to the router(s)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mikrotik-backup.git
cd mikrotik-backup
```

2. Install required dependencies:
```bash
pip install paramiko
```

## Configuration

Create a `config.json` file in the script directory with the following structure:

```json
{
    "backup_age": 30,
    "routers": [
        {
            "host": "192.168.88.1",
            "username": "admin",
            "password": "your_password",
            "port": 22
        },
        {
            "host": "192.168.88.2",
            "username": "admin",
            "password": "your_password",
            "port": 22
        }
    ]
}
```

### Configuration Parameters

- `backup_age`: Number of days to keep backups (default: 30)
- `routers`: Array of router configurations
  - `host`: Router IP address or hostname
  - `username`: SSH username
  - `password`: SSH password
  - `port`: SSH port (default: 22)

## Directory Structure

```
mikrotik_backups/
├── binary/
│   └── [hostname]_backup_[timestamp].backup
└── plaintext/
    └── [hostname]_config_[timestamp].rsc
```

## Usage

Run the script:
```bash
python mikrotik_backup.py
```

The script will:
1. Create backup directories if they don't exist
2. Connect to each router in the configuration
3. Create and download both binary and plaintext backups
4. Clean up old backups based on the specified retention period

## Backup Types

### Binary Backup (.backup)
- Complete system backup
- Includes all router settings
- Version-specific (can only be restored on similar RouterOS versions)
- Created using `/system backup save`

### Plaintext Backup (.rsc)
- Human-readable configuration script
- Portable between different RouterOS versions
- Can be manually edited if needed
- Created using `/export`

## Error Handling

The script includes comprehensive error handling for:
- SSH connection failures
- Backup creation errors
- File transfer issues
- Cleanup process errors

## Security Considerations

1. Store credentials securely
2. Use strong passwords
3. Consider using SSH keys instead of passwords
4. Restrict SSH access to specific IP addresses
5. Keep backup files in a secure location

## Maintenance

- Regular testing of backup files
- Monitoring of disk space usage
- Verification of backup integrity
- Review of backup retention period

## Troubleshooting

### Common Issues

1. SSH Connection Failed
   - Verify router IP address and credentials
   - Check SSH service status on router
   - Verify network connectivity

2. Permission Denied
   - Check user permissions on router
   - Verify credentials in config.json

3. Backup Creation Failed
   - Check available storage on router
   - Verify user permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MikroTik for RouterOS documentation
- Paramiko SSH library developers
- Community contributors

## Version History

- 1.0.0
  - Initial release
  - Basic backup functionality
  - Automatic cleanup
  - Multi-router support

## TODO

- [ ] Add SSH key authentication support
- [ ] Implement backup verification
- [ ] Add email notifications
- [ ] Add compression for long-term storage
- [ ] Create backup restoration script
- [ ] Add logging functionality

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Disclaimer

This tool is provided as-is with no warranty. Always test backups regularly and maintain multiple copies of critical configurations.