const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');
const { dialog } = require('electron');

/**
 * Check if a port is available
 * @param {number} port Port number
 * @returns {Promise<boolean>} Whether the port is busy
 */
function checkPort(port) {
  return new Promise(resolve => {
    const server = http.createServer();
    server.once('error', () => {
      resolve(true); // Port is busy
    });
    server.once('listening', () => {
      server.close();
      resolve(false); // Port is available
    });
    server.listen(port);
  });
}

/**
 * Find Python executable
 * @returns {string} Path to Python executable
 */
function findPythonExecutable() {
  const possiblePaths = [
    'python3',
    'python',
    '/usr/bin/python3',
    '/usr/local/bin/python3',
    'C:\\Python312\\python.exe',
    'C:\\Python311\\python.exe',
    'C:\\Python310\\python.exe',
    'C:\\Python39\\python.exe'
  ];

  // In production, check for bundled Python
  if (process.env.NODE_ENV !== 'development') {
    const bundledPython = path.join(process.resourcesPath, 'python', 'python');
    if (fs.existsSync(bundledPython)) {
      return bundledPython;
    }
    if (process.platform === 'win32') {
      const bundledPythonWin = path.join(process.resourcesPath, 'python', 'python.exe');
      if (fs.existsSync(bundledPythonWin)) {
        return bundledPythonWin;
      }
    }
  }

  // Try to find Python in PATH
  for (const pythonPath of possiblePaths) {
    try {
      const { execSync } = require('child_process');
      execSync(`${pythonPath} --version`, { stdio: 'ignore' });
      return pythonPath;
    } catch (error) {
      // Continue to next path
    }
  }

  return 'python3'; // Default fallback
}

/**
 * Get Python backend directory
 * @returns {string} Path to Python backend
 */
function getPythonBackendDir() {
  if (process.env.NODE_ENV === 'development') {
    return path.join(__dirname, '../../python-backend');
  } else {
    // In production, Python backend is bundled in resources
    return path.join(process.resourcesPath, 'python-backend');
  }
}

/**
 * Start Python backend server
 * @param {number} port Port number
 * @param {Object} app Electron app object
 * @returns {Promise<{url: string, process: ChildProcess}>} Server URL and process
 */
async function startPythonServer(port, app) {
  console.log(`Starting Easy Dataset Python backend, version: ${require('../util').getAppVersion()}`);

  // Set up log file path
  const logDir = path.join(app.getPath('userData'), 'logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  const logFile = path.join(logDir, `python-backend-${new Date().toISOString().replace(/:/g, '-')}.log`);
  const logStream = fs.createWriteStream(logFile, { flags: 'a' });

  // Check if port is already in use
  const isPortBusy = await checkPort(port);
  if (isPortBusy) {
    console.log(`Port ${port} is already in use, attempting to connect...`);
    return { url: `http://localhost:${port}`, process: null };
  }

  console.log(`Starting Python backend server on port: ${port}`);

  try {
    const pythonExecutable = findPythonExecutable();
    const backendDir = getPythonBackendDir();
    
    console.log(`Python executable: ${pythonExecutable}`);
    console.log(`Backend directory: ${backendDir}`);

    // Check if backend directory exists
    if (!fs.existsSync(backendDir)) {
      throw new Error(`Python backend directory not found: ${backendDir}`);
    }

    // Set up environment variables
    const env = {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      EASY_DATASET_DB_PATH: path.join(app.getPath('userData'), 'easy_dataset.db'),
      EASY_DATASET_UPLOAD_DIR: path.join(app.getPath('userData'), 'uploads'),
      EASY_DATASET_LOG_LEVEL: process.env.NODE_ENV === 'development' ? 'DEBUG' : 'INFO'
    };

    // Spawn Python process
    const pythonProcess = spawn(
      pythonExecutable,
      [
        '-m', 'uvicorn',
        'easy_dataset_server.app:app',
        '--host', '0.0.0.0',
        '--port', port.toString(),
        '--log-level', process.env.NODE_ENV === 'development' ? 'debug' : 'info'
      ],
      {
        cwd: backendDir,
        env: env,
        stdio: ['ignore', 'pipe', 'pipe']
      }
    );

    // Log stdout
    pythonProcess.stdout.on('data', (data) => {
      const message = data.toString();
      console.log(`[Python Backend] ${message}`);
      logStream.write(`[${new Date().toISOString()}] [STDOUT] ${message}\n`);
    });

    // Log stderr
    pythonProcess.stderr.on('data', (data) => {
      const message = data.toString();
      console.error(`[Python Backend Error] ${message}`);
      logStream.write(`[${new Date().toISOString()}] [STDERR] ${message}\n`);
    });

    // Handle process exit
    pythonProcess.on('exit', (code, signal) => {
      const message = `Python backend process exited with code ${code} and signal ${signal}`;
      console.log(message);
      logStream.write(`[${new Date().toISOString()}] ${message}\n`);
      logStream.end();
    });

    // Handle process errors
    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python backend:', error);
      logStream.write(`[${new Date().toISOString()}] [ERROR] ${error.message}\n`);
      dialog.showErrorBox(
        'Python Backend Error',
        `Failed to start Python backend: ${error.message}\n\nPlease ensure Python 3.9+ is installed.`
      );
    });

    // Wait for server to be ready
    const maxRetries = 30;
    let retries = 0;
    
    while (retries < maxRetries) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        const response = await new Promise((resolve, reject) => {
          const req = http.get(`http://localhost:${port}/health`, (res) => {
            resolve(res.statusCode === 200);
          });
          req.on('error', reject);
          req.setTimeout(1000, () => {
            req.destroy();
            reject(new Error('Timeout'));
          });
        });
        
        if (response) {
          console.log('Python backend is ready!');
          return { url: `http://localhost:${port}`, process: pythonProcess };
        }
      } catch (error) {
        // Server not ready yet, continue waiting
      }
      
      retries++;
    }

    throw new Error('Python backend failed to start within timeout period');

  } catch (error) {
    console.error('Failed to start Python backend:', error);
    logStream.write(`[${new Date().toISOString()}] [ERROR] ${error.message}\n`);
    logStream.end();
    
    dialog.showErrorBox(
      'Startup Failed',
      `Unable to start Python backend: ${error.message}\n\nPlease check:\n1. Python 3.9+ is installed\n2. Required packages are installed (pip install -e python-backend)\n3. Check logs at: ${logFile}`
    );
    
    app.quit();
    throw error;
  }
}

/**
 * Stop Python backend server
 * @param {ChildProcess} pythonProcess Python process to stop
 * @returns {Promise<void>}
 */
async function stopPythonServer(pythonProcess) {
  if (!pythonProcess) {
    return;
  }

  console.log('Stopping Python backend...');

  return new Promise((resolve) => {
    // Set a timeout for graceful shutdown
    const timeout = setTimeout(() => {
      console.log('Force killing Python backend process...');
      pythonProcess.kill('SIGKILL');
      resolve();
    }, 5000);

    pythonProcess.on('exit', () => {
      clearTimeout(timeout);
      console.log('Python backend stopped');
      resolve();
    });

    // Try graceful shutdown first
    pythonProcess.kill('SIGTERM');
  });
}

module.exports = {
  checkPort,
  startPythonServer,
  stopPythonServer,
  findPythonExecutable,
  getPythonBackendDir
};
