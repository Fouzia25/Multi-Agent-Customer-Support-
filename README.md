# Multi-Agent Customer Support

A Streamlit app where three CrewAI agents answer a customer query in sequence:

1. **Assistant**: answers from its own knowledge (no tools).
2. **Web Search Assistant**: searches the web (Serper) and answers with cited URLs.
3. **Entry Agent**: appends the query and both answers to `answers.txt`.

Requires **Python 3.10–3.13** (CrewAI does not support 3.14 yet), an
[OpenAI API key](https://platform.openai.com/api-keys) and a [Serper API key](https://serper.dev).

## macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY="sk-..."
export SERPER_API_KEY="..."
export OPENAI_MODEL_NAME="gpt-4o-mini"   # optional

streamlit run app.py
```

## Windows (PowerShell)

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:OPENAI_API_KEY="sk-..."
$env:SERPER_API_KEY="..."
$env:OPENAI_MODEL_NAME="gpt-4o-mini"   # optional

streamlit run app.py
```

Environment variables set this way last only for the current terminal session.
Every query is appended to `answers.txt`, which you can also download from the app.
