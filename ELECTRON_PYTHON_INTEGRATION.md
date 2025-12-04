# Electron + Python Backend Integration

This document describes how the Easy Dataset desktop application integrates the Python backend with Electron.

## Overview

The Easy Dataset desktop application uses:
- **Electron** for the desktop shell and window management
- **React + Next.js** for the frontend UI (unchanged from original)
- **Python FastAPI** for the backend API (converted from Node.js)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Electron Shell                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │           React Frontend (Browser Window)         │  │
│  │  - Next.js App                                    │  │
│  │  - Material-UI Components                         │  │
│  │  - Unchanged from original                        │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↕ HTTP/WebSocket                │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Python Backend (Subprocess)               │  │
│  │  - FastAPI Server                                 │  │
│  │  - SQLAlchemy ORM                                 │  │
│  │  - LLM Integrations                               │  │
│  │  - File Processing                                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Python Server Module (`electron/modules/python-server.js`)

Manages the Python backend process:

- **Finds Python executable** on the system
- **Spawns Python process** with uvicorn
- **Monitors process health** via `/health` endpoint
- **Handles graceful shutdown** on app exit
- **Logs output** to user data directory

**Key Functions:**
```javascript
startPythonServer(port, app)  // Start Python backend
stopPythonServer(process)     // Stop Python backend gracefully
findPythonExecutable()        // Locate Python on system
getPythonBackendDir()         // Get backend directory path
```

### 2. Main Process (`electron/main.js`)

Updated to launch Python backend:

**Development Mode:**
- Frontend runs separately (`npm run dev`)
- Python backend can run separately or be managed by Electron
- Opens DevTools for debugging

**Production Mode:**
- Starts Python backend automatically
- Waits for backend to be ready
- Loads frontend from backend server
- Handles graceful shutdown

### 3. Build Configuration (`package.json`)

Updated to include Python backend in builds:

```json
{
  "build": {
    "extraResources": [
      {
        "from": "python-backend",
        "to": "python-backend",
        "filter": ["**/*", "!**/__pycache__/**", ...]
      }
    ],
    "afterPack": "./scripts/afterPack.js"
  }
}
```

### 4. Build Scripts

**`scripts/prepare-python-build.js`**
- Validates Python installation
- Installs Python dependencies
- Cleans build artifacts
- Prepares backend for bundling

**`scripts/afterPack.js`**
- Runs after Electron packaging
- Verifies Python backend is included
- Platform-specific post-processing

## Startup Flow

### Development Mode

```
1. User runs: npm run electron-dev
2. Electron starts
3. Loads http://localhost:1717 (assumes frontend is running)
4. Python backend runs separately (optional)
```

### Production Mode

```
1. User launches Easy Dataset.app
2. Electron main process starts
3. Finds Python executable
4. Spawns Python backend process:
   python -m uvicorn easy_dataset_server.app:app --port 1717
5. Waits for /health endpoint to respond
6. Loads frontend from http://localhost:1717
7. Application ready
```

## Shutdown Flow

```
1. User closes window or quits app
2. Electron 'before-quit' event fires
3. Sends SIGTERM to Python process
4. Waits up to 5 seconds for graceful shutdown
5. If timeout, sends SIGKILL
6. Electron quits
```

## Environment Variables

The Python backend receives these environment variables:

```javascript
{
  PYTHONUNBUFFERED: '1',                    // Immediate output
  EASY_DATASET_DB_PATH: '<userData>/easy_dataset.db',
  EASY_DATASET_UPLOAD_DIR: '<userData>/uploads',
  EASY_DATASET_LOG_LEVEL: 'DEBUG' | 'INFO'
}
```

## Logging

### Python Backend Logs

Location: `<userData>/logs/python-backend-<timestamp>.log`

Contains:
- Startup messages
- HTTP requests
- Errors and exceptions
- Shutdown messages

### Electron Logs

Location: `<userData>/logs/`

Contains:
- Electron main process logs
- Python process management logs
- Update check logs

## Update System

### Electron App Updates

Uses `electron-updater` for Electron app updates:
- Checks GitHub releases
- Downloads and installs updates
- Prompts user to restart

### Python Backend Updates

Custom update system for Python backend:
- Checks for backend updates independently
- Downloads from GitHub releases
- Installs without full app reinstall
- Requires app restart to apply

See [UPDATE_SYSTEM.md](python-backend/UPDATE_SYSTEM.md) for details.

## Platform-Specific Considerations

### macOS

**Python Location:**
- `/usr/bin/python3` (system Python)
- `/usr/local/bin/python3` (Homebrew)
- Bundled in app: `Easy Dataset.app/Contents/Resources/python/`

**Backend Location:**
- `Easy Dataset.app/Contents/Resources/python-backend/`

**Permissions:**
- App must be signed for distribution
- Python backend included in signature

### Windows

**Python Location:**
- `C:\Python3X\python.exe`
- `python` or `python3` in PATH
- Bundled in app: `resources\python\python.exe`

**Backend Location:**
- `resources\python-backend\`

**Considerations:**
- Windows Defender may flag Python executable
- Installer should be signed

### Linux

**Python Location:**
- `/usr/bin/python3` (most distros)
- System Python usually available

**Backend Location:**
- `resources/python-backend/`

**Considerations:**
- AppImage includes all dependencies
- May need to install Python separately for .deb

## Troubleshooting

### Python Not Found

**Symptoms:**
- App fails to start
- Error: "Python not found"

**Solutions:**
1. Install Python 3.9+
2. Add Python to PATH
3. Check logs for Python search paths

### Backend Fails to Start

**Symptoms:**
- App shows connection error
- Backend logs show errors

**Solutions:**
1. Check Python dependencies installed
2. Verify port 1717 is available
3. Check backend logs for errors
4. Try running backend manually:
   ```bash
   cd python-backend
   uvicorn easy_dataset_server.app:app --port 1717
   ```

### Backend Crashes

**Symptoms:**
- App works initially, then fails
- Backend process exits unexpectedly

**Solutions:**
1. Check backend logs for exceptions
2. Verify database file is accessible
3. Check disk space
4. Update Python dependencies

### Slow Startup

**Symptoms:**
- App takes long time to start
- Timeout waiting for backend

**Solutions:**
1. Check Python startup time
2. Verify database initialization
3. Check for slow imports
4. Increase timeout in `python-server.js`

## Development Workflow

### Running in Development

**Option 1: Separate Processes**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Python Backend
cd python-backend
uvicorn easy_dataset_server.app:app --reload --port 1717

# Terminal 3: Electron
npm run electron
```

**Option 2: Electron Manages Backend**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Electron (starts backend automatically)
npm run electron-dev
```

### Testing Production Build

```bash
# Build for current platform
npm run electron-build-mac    # macOS
npm run electron-build-win    # Windows
npm run electron-build-linux  # Linux

# Test the built app
open dist/Easy\ Dataset.app   # macOS
```

### Debugging

**Python Backend:**
```python
# Add breakpoints in Python code
import pdb; pdb.set_trace()

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

**Electron:**
```javascript
// Open DevTools
mainWindow.webContents.openDevTools();

// Console logging
console.log("Debug message");
```

## Best Practices

1. **Always check Python version** before starting backend
2. **Handle backend crashes gracefully** with restart logic
3. **Log everything** for debugging production issues
4. **Test on all platforms** before release
5. **Include Python in installer** for better UX
6. **Monitor backend health** during runtime
7. **Provide clear error messages** to users

## Future Improvements

- [ ] Bundle Python interpreter with app
- [ ] Automatic backend restart on crash
- [ ] Better error reporting to user
- [ ] Performance monitoring
- [ ] Crash reporting integration
- [ ] Multiple backend instances for parallel processing

## References

- [Electron Documentation](https://www.electronjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Electron Builder](https://www.electron.build/)
- [Python Packaging](https://packaging.python.org/)
