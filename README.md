# 🧠 AI Agents Suite - MCP Web Scraper & Developer Tools Research

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-green.svg)](https://www.langchain.com/langgraph)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange.svg)](https://groq.com)
[![Firecrawl](https://img.shields.io/badge/Firecrawl-Scraper-red.svg)](https://firecrawl.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A powerful suite of AI agents for web scraping, developer tools research, and intelligent data extraction using MCP protocol and Llama-4**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Projects](#projects)
  - [Agent 1: MCP Web Scraper Agent](#agent-1-mcp-web-scraper-agent)
  - [Agent 2: Developer Tools Research Agent](#agent-2-developer-tools-research-agent)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Use Cases](#use-cases)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This repository contains **two intelligent AI agents** built with LangGraph, MCP (Model Context Protocol), and Groq's Llama-4 model. These agents can:

- **Scrape and understand any website** through natural conversation
- **Research developer tools** and extract structured information
- **Compare alternatives** for any technology or service
- **Generate structured reports** with pricing, tech stack, and integrations

### Key Features

| Feature | Agent 1 | Agent 2 |
|---------|:-------:|:-------:|
| Web Scraping | ✅ | ✅ |
| Natural Language Interface | ✅ | ❌ |
| Batch Research | ❌ | ✅ |
| Structured Output (JSON) | ❌ | ✅ |
| Competitor Analysis | ❌ | ✅ |
| Pricing Extraction | ❌ | ✅ |

---

## 🤖 Projects

### Agent 1: MCP Web Scraper Agent

**File:** `simple-agent/main.py`

An interactive conversational agent that scrapes websites using Firecrawl MCP server.

#### What it does:
- Chat with the agent about any website
- Agent automatically decides when to scrape
- Extracts and summarizes web content
- Handles tool calling errors gracefully
