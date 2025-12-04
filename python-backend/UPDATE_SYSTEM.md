# Python Backend Update System

This document describes the auto-update system for the Python backend in the Easy Dataset desktop application.

## Overview

The update system allows the Python backend to be updated independently of the Electron application. This provides flexibility for bug fixes and feature updates without requiring a full application reinstall.

## Architecture

### Components

1. **Backend Updater (`easy_dataset/utils/updater.py`)**
   - Core update logic
   - Version comparison
   - Download and installation

2. **Update API (`easy_dataset_server/api/updates.py`)**
   - REST endpoints for update operations
   - `/api/updates/check` - Check for updates
   - `/api/updates/download` - Download update
   - `/api/updates/install` - Install update
   - `/api/updates/version` - Get current version

3. **Electron Integration (`electron/modules/python-updater.js`)**
   - IPC handlers for update operations
   - User prompts and progress display
   - Application restart handling

## Update Flow

```
1. Check for Updates
   ├─> Query GitHub Releases API
   ├─> Compare versions
   └─> Return update info if available

2. Download Update
   ├─> Download from GitHub
   ├─> Show progress
   └─> Save to temp directory

3. Verify Update (optional)
   ├─> Calculate SHA256 hash
   └─> Compare with expected hash

4. Install Update
   ├─> Create backup of current installation
   ├─> Extract update files
   ├─> Verify installation
   └─> Restore backup if failed

5. Restart Application
   └─> Apply new version
```

## Usage

### Automatic Updates

The application automatically checks for updates 10 seconds after startup:

```javascript
// In electron/main.js
setTimeout(() => {
  handleBackendUpdate(backendVersion, mainWindow, port);
}, 10000);
```

### Manual Update Check

Users can manually check for updates through the UI:

```javascript
// From renderer process
const updateInfo = await window.electron.ipcRenderer.invoke(
  'check-backend-update',
  currentVersion,
  port
);

if (updateInfo && updateInfo.update_available) {
  // Show update notification
  await window.electron.ipcRenderer.invoke(
    'handle-backend-update',
    currentVersion,
    port
  );
}
```

### API Usage

You can also check for updates directly via the API:

```bash
# Check for updates
curl http://localhost:1717/api/updates/check?current_version=2.0.0

# Get current version
curl http://localhost:1717/api/updates/version
```

## Version Management

### Version Format

Versions follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Version Comparison

The updater compares versions numerically:

```python
"2.1.0" > "2.0.0"  # True (newer minor version)
"2.0.1" > "2.0.0"  # True (newer patch version)
"2.0.0" > "2.0.0"  # False (same version)
```

## Release Process

### Creating a Release

1. **Update Version**
   ```python
   # In easy_dataset_server/config.py
   app_version = "2.1.0"
   ```

2. **Build Distribution**
   ```bash
   cd python-backend
   python -m build
   ```

3. **Create GitHub Release**
   - Tag: `v2.1.0`
   - Title: `Python Backend v2.1.0`
   - Upload: `dist/easy_dataset-2.1.0.tar.gz`
   - Asset name must contain "python-backend"

4. **Test Update**
   ```bash
   # Check for updates
   curl http://localhost:1717/api/updates/check?current_version=2.0.0
   ```

### Release Asset Naming

The update system looks for assets containing "python-backend" in the name:

- ✅ `python-backend-2.1.0.zip`
- ✅ `easy-dataset-python-backend-2.1.0.tar.gz`
- ❌ `backend-2.1.0.zip` (missing "python-backend")

## Configuration

### Update Server URL

By default, updates are checked from GitHub:

```python
update_server_url = "https://api.github.com/repos/ConardLi/easy-dataset/releases"
```

To use a custom update server:

```python
from easy_dataset.utils.updater import BackendUpdater

updater = BackendUpdater(
    update_server_url="https://your-server.com/api/releases",
    current_version="2.0.0"
)
```

### Update Check Interval

Configure in `electron/main.js`:

```javascript
// Check every 10 seconds (default)
setTimeout(() => {
  handleBackendUpdate(backendVersion, mainWindow, port);
}, 10000);

// Check every hour
setTimeout(() => {
  handleBackendUpdate(backendVersion, mainWindow, port);
}, 3600000);
```

## Security

### Hash Verification

Updates can be verified using SHA256 hashes:

```python
updater = BackendUpdater()
update_file = updater.download_update(download_url)

# Verify with expected hash
if updater.verify_update(update_file, expected_hash="abc123..."):
    updater.install_update(update_file)
```

### Backup and Rollback

The installer automatically creates a backup before updating:

```
installation_dir/
├── easy_dataset/          # Current installation
└── easy_dataset_backup/   # Backup (created before update)
```

If installation fails, the backup is automatically restored.

## Troubleshooting

### Update Check Fails

**Problem:** Cannot check for updates

**Solutions:**
1. Check internet connection
2. Verify GitHub API is accessible
3. Check logs: `~/.config/Easy Dataset/logs/`

### Download Fails

**Problem:** Update download fails or times out

**Solutions:**
1. Check available disk space
2. Verify download URL is accessible
3. Try manual download and install

### Installation Fails

**Problem:** Update installation fails

**Solutions:**
1. Check file permissions
2. Ensure application is not running
3. Manually restore from backup:
   ```bash
   mv easy_dataset_backup easy_dataset
   ```

### Version Not Detected

**Problem:** Current version not detected correctly

**Solutions:**
1. Check `easy_dataset_server/config.py`
2. Verify version format (e.g., "2.0.0")
3. Restart application

## Development

### Testing Updates Locally

1. **Create Test Release**
   ```bash
   cd python-backend
   python -m build
   zip -r python-backend-test.zip dist/
   ```

2. **Mock Update Server**
   ```python
   # Create mock server that returns update info
   from fastapi import FastAPI
   
   app = FastAPI()
   
   @app.get("/releases")
   def get_releases():
       return [{
           "tag_name": "v2.1.0",
           "body": "Test release",
           "assets": [{
               "name": "python-backend-2.1.0.zip",
               "browser_download_url": "http://localhost:8000/download"
           }]
       }]
   ```

3. **Test Update Flow**
   ```python
   from easy_dataset.utils.updater import BackendUpdater
   
   updater = BackendUpdater(
       update_server_url="http://localhost:8000/releases",
       current_version="2.0.0"
   )
   
   update_info = updater.check_for_updates()
   print(update_info)
   ```

### Adding Update Notifications

To add custom update notifications in the UI:

```javascript
// Listen for update events
window.electron.ipcRenderer.on('update-progress', (event, message) => {
  console.log('Update progress:', message);
  // Show notification in UI
});
```

## Best Practices

1. **Always test updates** in a development environment first
2. **Create backups** before major updates
3. **Use semantic versioning** for clear version communication
4. **Include release notes** to inform users of changes
5. **Monitor update success rates** to catch issues early
6. **Provide rollback mechanism** for failed updates

## Future Enhancements

- [ ] Delta updates (only download changed files)
- [ ] Automatic rollback on startup failure
- [ ] Update scheduling (install at specific time)
- [ ] Multiple update channels (stable, beta, dev)
- [ ] Update size optimization
- [ ] Offline update support

## References

- [Semantic Versioning](https://semver.org/)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)
- [Electron Auto Updater](https://www.electronjs.org/docs/latest/api/auto-updater)
