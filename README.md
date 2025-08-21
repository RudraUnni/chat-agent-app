# Medical Assistant

A medical research assistant powered by PubMed database integration and AI-driven analysis.

## Overview

This application provides a chat interface for medical research queries, leveraging the PubMed database to provide evidence-based medical information. The system uses a multi-agent workflow to search, analyze, and synthesize medical literature.

## Features

- **Medical Research**: Access to PubMed database for evidence-based medical information
- **Real-time Chat**: WebSocket-powered chat interface with streaming responses
- **Markdown Support**: Rich text formatting for medical literature and research findings
- **Multi-agent Workflow**: Sophisticated backend processing with specialized medical agents

## Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database for user sessions and chat history
- **Multi-agent System** - Specialized agents for PubMed research and analysis
- **WebSocket Support** - Real-time streaming responses

### Frontend
- **React + TypeScript** - Modern frontend framework
- **Tailwind CSS** - Utility-first styling
- **Redux Toolkit** - State management
- **React Markdown** - Rich text rendering for medical content

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (for PostgreSQL)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
docker-compose up -d  # Start PostgreSQL
python -m app.main    # Start FastAPI server
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Start development server
```

## Usage

1. Navigate to the frontend application
2. Start a conversation by typing a medical question
3. The system will search PubMed and provide evidence-based responses
4. Chat history is maintained across sessions

## Configuration

Key configuration options in `backend/app/core/config.py`:
- `pubmed_max_results`: Maximum number of PubMed results to fetch
- `default_llm_model`: AI model for text generation
- Database connection settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.