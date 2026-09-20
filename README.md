# JavaChat

JavaChat is an AI-powered Java learning assistant built with Streamlit and Google's Gemini API. It helps beginners and intermediate learners understand Java concepts, review code, debug errors, practice exam questions, and solve programming problems.

## Features

- Conversational Java assistant with chat history
- Multiple chat sessions during a Streamlit session
- Java learning topics and guided prompts
- Code Lab for explaining, debugging, and improving Java code
- Exam Practice prompts for theory and programming questions
- Optional local Java knowledge base from `java.txt`
- Automatic discovery of compatible text-generation models
- Friendly handling for missing keys, unavailable models, permissions, and quota limits
- Dark responsive interface

## Project structure

```text
java-chat-app/
├── app.py
├── java.txt
├── check_models.py
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── secrets.toml       # local only; never commit this file
```

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- Streamlit
- The `google-genai` Python package

## Run locally

Clone the repository and enter the project:

```bash
git clone https://github.com/viniskumar2007-lgtm/java-chat-app.git
cd java-chat-app
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux, macOS, or Codespaces

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configure the Gemini API key

Create the Streamlit secrets file:

```bash
mkdir -p .streamlit
rm -rf .streamlit/secrets.toml
```

Create `.streamlit/secrets.toml` with this content:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

On Windows PowerShell, you can open the file with:

```powershell
New-Item -ItemType Directory -Force .streamlit
notepad .streamlit\secrets.toml
```

The key can also be provided through the `GEMINI_API_KEY` environment variable.

Get or manage a key at:

<https://aistudio.google.com/app/apikey>

Never commit or share `.streamlit/secrets.toml`. The repository `.gitignore` excludes it.

## Start the app

```bash
python -m streamlit run app.py
```

Open the local URL shown by Streamlit, normally:

```text
http://localhost:8501
```

In GitHub Codespaces, open the **PORTS** panel, find port `8501`, and choose **Open in Browser**.

## Check available models

JavaChat discovers compatible text-generation models automatically. To inspect the models available to your key:

```bash
python check_models.py
```

The key must have access to a model supporting `generateContent`. Audio-only TTS models, image models, embedding models, and other incompatible models are ignored.

## Knowledge base

`java.txt` contains Java reference material used to add relevant context to prompts. You can replace or extend it with your own Java notes. Keep the file focused and reasonably sized to reduce token usage.

## Quota errors

Gemini free-tier keys have rate and token limits. A `429 RESOURCE_EXHAUSTED` response means the current quota has been exceeded temporarily. Wait for the retry period shown by the app, shorten large prompts, or review your usage and billing:

- <https://ai.dev/rate-limit>
- <https://ai.google.dev/gemini-api/docs/rate-limits>

## Security

- Keep API keys only in `.streamlit/secrets.toml` or environment variables.
- Never paste an API key into `app.py`, `java.txt`, screenshots, issues, or pull requests.
- If a key is exposed, revoke it immediately and create a replacement.
- Do not commit virtual environments or generated Python cache files.

## License

Add the license that matches how you want to distribute this project before publishing it publicly.
