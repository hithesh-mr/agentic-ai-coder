# Agentic AI Coder (Plain-JS Extension)

This is a minimal JavaScript-only VS Code extension scaffold to get started without Node/npm installs.

## Commands

- Agentic Coder: Hello (`agenticCoder.hello`)
- Agentic Coder: Ping Backend (`agenticCoder.pingBackend`)

## Settings

- `agenticCoder.backendBaseUrl` (default `http://127.0.0.1:5000`)

## Run

1. Start any test backend you want to ping (optional), e.g. `python test-project/backend/app.py`.
2. In VS Code, press F5 or run the launch config "Run Agentic AI Coder Extension".
3. In the Extension Development Host:
   - Run "Agentic Coder: Hello" to verify the extension is active.
   - Run "Agentic Coder: Ping Backend" to call `<backendBaseUrl>/api/todos` and see the result.

No TypeScript or bundling is required for this scaffold.
