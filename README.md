# Genealogy Agent (OpenAI + Claude Compatible)

This repository includes a working foundation for an expert-grade genealogy assistant that can:

- parse **GEDCOM** records,
- process **handwritten PDF extraction** with a bundled open-source OCR/HTR adapter,
- fetch and extract text from **webpages**,
- query **historical context** through an MCP-style client interface,
- enforce **evidence-first** rules with citations and human-in-the-loop review.

## Core architecture

- `GenealogyAgent` orchestrates research flows.
- `LLMBackend` provides model-provider portability.
- Tooling modules provide capability-specific integrations:
  - `tools/gedcom.py`
  - `tools/documents.py`
  - `tools/web.py`
  - `tools/historical_context.py`

## Handwritten PDFs: included default adapter

You **do not** need to write your own adapter to get started.

This package includes `KrakenPdfReader`, a built-in integration for the open-source [Kraken OCR/HTR](https://github.com/mittagessen/kraken) stack (widely used on historical/archival handwriting).

Install OCR extra dependencies:

```bash
pip install -e .[ocr]
```

Then configure it in the agent:

```python
from genealogy_agent import GenealogyAgent
from genealogy_agent.providers import OpenAIBackend
from genealogy_agent.tools import KrakenPdfReader

agent = GenealogyAgent(
    backend=OpenAIBackend(),
    pdf_reader=KrakenPdfReader(model_path="/models/kraken/best.mlmodel", language="de"),
)
```

## What this solves from your requirements

1. **GEDCOM support**
   - `parse_gedcom` builds a tree structure for downstream family-link analysis.
2. **Handwritten PDFs in many languages**
   - `KrakenPdfReader` is built in for open-source HTR.
   - `ConfigurablePdfReader` remains available if you want a different engine later.
3. **Historical context (MCP use)**
   - `MCPClient` protocol + `DictMCPClient` reference implementation.
4. **Web access for archives**
   - `WebBrowserTool` fetches and extracts plain text snippets for analysis.

## Research governance built in

- Every flow tracks `resources_examined` and writes structured logs.
- Discoveries include confidence + citations.
- Lower-confidence findings are marked for human review.
- Human decisions convert discovery status to `verified` or `rejected`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[ocr]
python -m pytest -q
```
