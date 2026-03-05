# AI QA Agent

AI-powered agent for API and Web UI testing.

## Quick Start

1. Copy `.env.example` to `.env` and add your OpenAI API key.
2. Build and run with Docker:
   ```bash
   docker-compose up --build
   ```
For development, install dependencies locally:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   ```
