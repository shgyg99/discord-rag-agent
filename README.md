# Discord RAG Agent

A Discord bot that uses Retrieval-Augmented Generation (RAG) to provide intelligent responses based on your document knowledge base.

## Features

- 🤖 Discord bot integration with slash commands
- 📚 Document-based knowledge retrieval
- 🔍 Semantic search using sentence transformers
- 💾 Embedding cache for improved performance
- 🚀 FAISS vector store for fast similarity search
- ⚡ Streaming responses from OpenRouter API
- 📊 Built-in metrics collection

## Prerequisites

- Python 3.12+
- Discord Bot Token
- OpenRouter API Key
- Docker (optional)

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Discord Configuration
DISCORD_TOKEN=your_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_CHANNEL_ID=your_channel_id_here

# OpenRouter Configuration
OPENROUTER_API_KEY=your_api_key_here
SITE_URL=your_site_url_here
SITE_NAME=your_site_name_here

# Proxy Configuration (Optional)
PROXY_URL=socks5://127.0.0.1:12334
```

## Installation

### Local Setup

1. Clone the repository
```bash
git clone <repository-url>
cd discord-rag-agent
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Add your documents to the `docs` directory

5. Run the bot
```bash
python src/main.py
```

### Docker Setup

1. Build the image
```bash
docker build -t discord-rag-agent .
```

2. Run the container
```bash
docker run -v $(pwd)/docs:/app/docs -v $(pwd)/logs:/app/logs --env-file .env discord-rag-agent
```

## Usage

The bot supports the following slash commands:

- `/ask <question>` - Ask a question about the documents
- `/help` - Display help information

## Project Structure

```
discord-rag-agent/
├── src/
│   ├── bot/
│   │   └── discord_client.py
│   ├── config/
│   │   └── settings.py
│   ├── rag/
│   │   └── agent.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── metrics.py
│   └── main.py
├── docs/           # Add your knowledge base documents here
├── logs/           # Log files directory
├── cache/          # Cache directory for embeddings
├── Dockerfile
├── requirements.txt
└── .env
```

## Metrics and Logging

- Logs are stored in the `logs` directory in JSON format
- Metrics include response latencies and usage statistics
- Embeddings are cached to improve performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
