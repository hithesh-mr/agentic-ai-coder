# Agentic AI Coder
Agentic AI Coder is an AI-powered coding assistant that transforms natural language prompts into executable code, enhancing developer productivity and code quality. It automates code generation, debugging, and optimization tasks, providing real-time suggestions and context-aware assistance.

## High-Level Architecture
```mermaid
graph TD;
  U["Developer in VSCode"] --> E["VSCode Extension (TS)"];
  E --> U;
  E --> B["Backend API"];
  B --> E;
  B --> L["LLM Inference (Azure OpenAI)"];
  B --> K["Knowledge Graph / Context Store"];
  K --> B;
  K --> S["Storage (Graph DB / Vector / Blob)"];
  S --> K;
  B --> V["Validation / Linters / Translators"];
  E -.-> LC["Local Cache (project files, versions, history)"];
  subgraph CrossCutting
    X["Auth/Security"]:::aux;
    T["Logging/Telemetry"]:::aux;
    CI["CI/CD & Versioning"]:::aux;
  end
  classDef aux fill:#f0f0f0,stroke:#bbb,color:#333;
```
