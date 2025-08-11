# MCP Text Extractor

This repository provides a curses-based CLI that guides users through extracting text from multiple sources and a Cloudflare Worker that performs the extraction and stores results in R2. The tool can process data from R2 buckets, local files, or website URLs and optionally generate embeddings, RAG-formatted output, and AI-style summaries.

## Setup

### Python CLI
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Ensure you have network access to a deployed worker or start one locally with Wrangler (see below).

### Cloudflare Worker
1. Install dependencies and Wrangler:
   ```bash
   npm install
   npm install -g wrangler
   ```
2. Develop locally:
   ```bash
   wrangler dev
   ```
3. Deploy to Cloudflare:
   ```bash
   wrangler publish
   ```

## Usage

Run the CLI to choose input sources and processing options:
```bash
python cli.py
```
The menu uses arrow keys and Enter to navigate prompts. Results are saved in the specified R2 bucket and, if selected, written to files in the current directory.

## Testing

Run unit tests for the worker:
```bash
npm test
```

## Edge Optimizations

The worker executes on Cloudflare's edge network, enabling low-latency access to R2 and rapid processing close to users.
