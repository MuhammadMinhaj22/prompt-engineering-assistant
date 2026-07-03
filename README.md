# Prompt Engineering Assistant

A web application for optimizing prompts using advanced prompt engineering techniques, powered by NVIDIA Nemotron 3 Ultra via OpenRouter.

## Features

- **5 Prompt Techniques**: Chain of Thought, Few-Shot, Zero-Shot, Role Prompting, ReAct
- **Side-by-Side Comparison**: View original vs optimized prompts
- **Explanations**: Get detailed reasoning for why optimizations work
- **Dark Theme UI**: Clean, modern interface
- **Copy to Clipboard**: Easy copying of prompts
- **Keyboard Shortcut**: Ctrl/Cmd + Enter to optimize

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **AI Model**: NVIDIA Nemotron 3 Ultra (via OpenRouter free tier)
- **Deployment**: Gunicorn for production

## Prerequisites

- Python 3.10+
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai))

## Setup

### 1. Clone and Navigate

```bash
cd D:\MINHAJ\AI Prompt Assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your free API key from [openrouter.ai/keys](https://openrouter.ai/keys)

### 5. Run the Application

**Development:**
```bash
python app.py
```

**Production:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 6. Access the App

Open http://localhost:5000 in your browser.

## Usage

1. **Enter your prompt** in the text area
2. **Select a technique** from the dropdown:
   - **Chain of Thought** - Step-by-step reasoning for complex problems
   - **Few-Shot** - Example-driven for structured outputs
   - **Zero-Shot** - Clear standalone instructions
   - **Role Prompting** - Expert persona assignment
   - **ReAct** - Reasoning + Acting cycles for multi-step tasks
3. **Click "Optimize Prompt"** to generate the improved version
4. **Click "Explain Improvements"** to understand what changed and why
5. **Copy** either prompt using the copy buttons

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter` — Optimize prompt

## Project Structure

```
AI Prompt Assistant/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md              # This file
└── templates/
    └── index.html         # Frontend UI
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend |
| POST | `/api/optimize` | Optimize prompt with technique |
| POST | `/api/explain` | Explain optimization |
| GET | `/api/techniques` | List available techniques |

## Example Requests

**Optimize:**
```bash
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python function to validate emails", "technique": "chain_of_thought"}'
```

**Explain:**
```bash
curl -X POST http://localhost:5000/api/explain \
  -H "Content-Type: application/json" \
  -d '{"original": "Write a Python function to validate emails", "optimized": "...", "technique": "Chain of Thought"}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OPENROUTER_API_KEY not set" | Create `.env` file with your API key |
| "API error: 401" | Verify your OpenRouter API key is valid |
| "API error: 429" | Rate limited - wait and retry |
| Port 5000 in use | Change port in `app.py` or kill existing process |

## License

MIT License - Feel free to use and modify for your projects.
