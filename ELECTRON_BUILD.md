# Electron Desktop Application Build Guide

This guide explains how to build the Easy Dataset desktop application with the Python backend.

## Prerequisites

### Required Software

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/

2. **Python** (3.9 or higher)
   - Download from: https://www.python.org/downloads/
   - Make sure Python is added to PATH

3. **pnpm** (Package Manager)
   ```bash
   npm install -g pnpm
   ```

### Platform-Specific Requirements

#### macOS
- Xcode Command Line Tools
  ```bash
  xcode-select --install
  ```

#### Windows
- Windows Build Tools
  ```bash
  npm install --global windows-build-tools
  ```

#### Linux
- Build essentials
  ```bash
  sudo apt-get install build-essential
  ```

## Build Process

### 1. Install Dependencies

```bash
# Install Node.js dependencies
pnpm install

# Install Python backend dependencies
cd python-backend
pip install -e .
cd ..
```

### 2. Prepare for Build

The build scripts will automatically:
- Install Python dependencies
- Clean build artifacts
- Prepare the Python backend
- Build the Next.js frontend
- Package everything with Electron

### 3. Build for Your Platform

#### Build for macOS
```bash
pnpm run electron-build-mac
```

This creates:
- `dist/Easy Dataset-{version}.dmg` - DMG installer
- `dist/Easy Dataset-{version}-arm64.dmg` - Apple Silicon
- `dist/Easy Dataset-{version}-x64.dmg` - Intel

#### Build for Windows
```bash
pnpm run electron-build-win
```

This creates:
- `dist/Easy Dataset Setup {version}.exe` - NSIS installer

#### Build for Linux
```bash
pnpm run electron-build-linux
```

This creates:
- `dist/Easy Dataset-{version}.AppImage` - AppImage
- `dist/easy-dataset_{version}_amd64.deb` - Debian package

#### Build for All Platforms
```bash
pnpm run electron-build
```

**Note:** Cross-platform builds may not work on all systems. It's recommended to build on the target platform.

## Build Output

All build artifacts are placed in the `dist/` directory:

```
dist/
├── Easy Dataset-{version}.dmg          # macOS installer
├── Easy Dataset Setup {version}.exe    # Windows installer
├── Easy Dataset-{version}.AppImage     # Linux AppImage
└── ...                                 # Other platform-specific files
```

## Development Mode

To run the application in development mode:

```bash
# Terminal 1: Start Next.js frontend
pnpm run dev

# Terminal 2: Start Python backend (optional, if not using Node.js backend)
cd python-backend
uvicorn easy_dataset_server.app:app --reload --port 8000

# Terminal 3: Start Electron
pnpm run electron-dev
```

## Troubleshooting

### Python Not Found

**Error:** `Python not found`

**Solution:**
1. Ensure Python 3.9+ is installed
2. Verify Python is in PATH:
   ```bash
   python3 --version
   # or
   python --version
   ```
3. On Windows, you may need to use `py` instead:
   ```bash
   py --version
   ```

### Build Fails on Python Dependencies

**Error:** `Failed to install Python dependencies`

**Solution:**
1. Manually install Python backend:
   ```bash
   cd python-backend
   pip install -e .
   ```
2. Verify installation:
   ```bash
   python -c "import easy_dataset; print('OK')"
   ```

### Electron Build Fails

**Error:** Various Electron Builder errors

**Solution:**
1. Clean the build directory:
   ```bash
   pnpm run clean-dist
   ```
2. Clear npm cache:
   ```bash
   pnpm store prune
   ```
3. Reinstall dependencies:
   ```bash
   rm -rf node_modules
   pnpm install
   ```

### Python Backend Not Starting in Production

**Error:** Application starts but shows connection error

**Solution:**
1. Check logs in:
   - macOS: `~/Library/Application Support/Easy Dataset/logs/`
   - Windows: `%APPDATA%\Easy Dataset\logs\`
   - Linux: `~/.config/Easy Dataset/logs/`
2. Verify Python backend is bundled:
   - Check `resources/python-backend/` in the app directory
3. Ensure Python is installed on the target system

## Build Configuration

The build configuration is in `package.json` under the `build` key:

```json
{
  "build": {
    "appId": "com.easydataset.app",
    "productName": "Easy Dataset",
    "extraResources": [
      {
        "from": "python-backend",
        "to": "python-backend",
        "filter": ["**/*", "!**/__pycache__/**", ...]
      }
    ],
    ...
  }
}
```

### Customizing the Build

To customize the build:

1. **Change App Name:** Edit `productName` in `package.json`
2. **Change App ID:** Edit `appId` in `package.json`
3. **Add Files:** Add to `files` or `extraResources` array
4. **Platform Settings:** Edit `mac`, `win`, or `linux` sections

## Code Signing (Optional)

For distribution, you should code sign your application:

### macOS
1. Get an Apple Developer certificate
2. Set environment variables:
   ```bash
   export CSC_LINK=/path/to/certificate.p12
   export CSC_KEY_PASSWORD=your_password
   ```

### Windows
1. Get a code signing certificate
2. Set environment variables:
   ```bash
   set CSC_LINK=C:\path\to\certificate.pfx
   set CSC_KEY_PASSWORD=your_password
   ```

## Publishing

To publish updates:

1. Update version in `package.json`
2. Build for all platforms
3. Upload to GitHub Releases or your update server
4. The auto-updater will notify users of new versions

## Additional Resources

- [Electron Builder Documentation](https://www.electron.build/)
- [Electron Documentation](https://www.electronjs.org/docs)
- [Python Packaging Guide](https://packaging.python.org/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/ConardLi/easy-dataset/issues
- Documentation: See README.md
