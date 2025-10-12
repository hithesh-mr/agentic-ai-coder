// Plain-JS VS Code Extension entrypoint
// Provides two commands:
//  - Agentic Coder: Hello (agenticCoder.hello)
//  - Agentic Coder: Ping Backend (agenticCoder.pingBackend)

const vscode = require('vscode');
const http = require('http');
const https = require('https');
const { URL } = require('url');

function httpGetJson(urlStr, timeoutMs = 8000) {
  return new Promise((resolve, reject) => {
    try {
      const url = new URL(urlStr);
      const isHttps = url.protocol === 'https:';
      const lib = isHttps ? https : http;

      const req = lib.request(
        {
          method: 'GET',
          hostname: url.hostname,
          port: url.port || (isHttps ? 443 : 80),
          path: url.pathname + url.search,
          headers: { 'Accept': 'application/json' },
          timeout: timeoutMs
        },
        (res) => {
          let data = '';
          res.setEncoding('utf8');
          res.on('data', (chunk) => (data += chunk));
          res.on('end', () => {
            if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
              try {
                const json = data ? JSON.parse(data) : null;
                resolve(json);
              } catch (e) {
                reject(new Error(`Failed to parse JSON: ${e.message}`));
              }
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${data || 'No body'}`));
            }
          });
        }
      );

      req.on('error', (err) => reject(err));
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timed out'));
      });
      req.end();
    } catch (e) {
      reject(e);
    }
  });
}

function activate(context) {
  const hello = vscode.commands.registerCommand('agenticCoder.hello', () => {
    vscode.window.showInformationMessage('Agentic Coder: Hello!');
  });

  const ping = vscode.commands.registerCommand('agenticCoder.pingBackend', async () => {
    const cfg = vscode.workspace.getConfiguration('agenticCoder');
    const base = (cfg.get('backendBaseUrl') || 'http://127.0.0.1:5000').replace(/\/+$/, '');
    const url = `${base}/api/todos`;

    const progressOpts = { location: vscode.ProgressLocation.Notification, title: 'Pinging backend...', cancellable: false };

    await vscode.window.withProgress(progressOpts, async () => {
      try {
        const json = await httpGetJson(url);
        const count = Array.isArray(json) ? json.length : (json ? 1 : 0);
        vscode.window.showInformationMessage(`Backend OK: ${url} (items: ${count})`);
      } catch (err) {
        vscode.window.showErrorMessage(`Backend ping failed: ${url} -> ${err.message}`);
      }
    });
  });

  context.subscriptions.push(hello, ping);
}

function deactivate() {}

module.exports = { activate, deactivate };
