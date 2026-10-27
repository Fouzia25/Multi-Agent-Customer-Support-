# Multi-Agent Customer Support

A customer support web app where **three AI agents work together** to answer a question.
It is built with [CrewAI](https://www.crewai.com/) (the agents) and [Streamlit](https://streamlit.io/) (the web page).

You type a question, and you get two answers side by side: one from the AI's own knowledge
and one researched on the web with sources. Both are saved to a log file, `answers.txt`.

---

## Table of contents

1. [How it works](#1-how-it-works)
2. [What you need before you start](#2-what-you-need-before-you-start)
3. [Get your API keys](#3-get-your-api-keys)
4. [Download the project](#4-download-the-project)
5. [Create a virtual environment](#5-create-a-virtual-environment)
6. [Install the dependencies](#6-install-the-dependencies)
7. [Set your API keys](#7-set-your-api-keys)
8. [Run the app](#8-run-the-app)
9. [Use the app](#9-use-the-app)
10. [Running it again later](#10-running-it-again-later)
11. [Troubleshooting](#11-troubleshooting)
12. [Project structure](#12-project-structure)

---

## 1. How it works

The three agents run **one after another** (CrewAI's sequential process):

| Order | Agent | What it does | Tools |
|---|---|---|---|
| 1 | **Assistant** | Answers the question from its own knowledge. | None |
| 2 | **Web Search Assistant** | Searches Google (through Serper), then writes an answer based on the results and lists the source URLs. | `SerperDevTool` |
| 3 | **Entry Agent** | Receives both earlier answers and saves the question, Answer 1 and Answer 2 to `answers.txt`. | `save_answers` |

The flow of data:

```
Your question
   │
   ├──► Agent 1: Assistant ──────────────► Answer 1 ─┐
   │                                                 │
   ├──► Agent 2: Web Search Assistant ───► Answer 2 ─┤
   │                                                 ▼
   └──► Agent 3: Entry Agent (receives Answer 1 + Answer 2) ──► answers.txt
```

The web page then shows Answer 1 and Answer 2 next to each other.

---

## 2. What you need before you start

- **Python 3.10, 3.11, 3.12 or 3.13.**
  ⚠️ Python **3.14 does not work**, because CrewAI does not support it yet.
  Check your version:
  - macOS/Linux: `python3 --version`
  - Windows: `py --list` (shows every installed version)

  If you don't have a supported version:
  - **Windows:** run `py install 3.13`, or download Python 3.13 from [python.org](https://www.python.org/downloads/).
    If you use the python.org installer, tick **"Add python.exe to PATH"**.
  - **macOS:** `brew install python@3.13`, or download it from [python.org](https://www.python.org/downloads/).
  - **Linux:** install `python3.13` and `python3.13-venv` with your package manager.
- **Git**, to download the project ([git-scm.com](https://git-scm.com/downloads)). You can also download the ZIP instead (see step 4).
- **An internet connection.**
- **Two API keys** (next step).

---

## 3. Get your API keys

You need **two** keys. Keep them private: never share them or upload them to GitHub.

### 3.1 OpenAI API key (for the AI agents)

1. Go to <https://platform.openai.com/api-keys> and sign in.
2. Click **"Create new secret key"** and copy it. It starts with `sk-`.
3. Make sure your OpenAI account has billing or credits set up, or requests will fail.

### 3.2 Serper API key (for web search)

1. Go to <https://serper.dev> and sign up. New accounts get free search credits.
2. Open the **API Key** page in the dashboard and copy your key.

> ⚠️ **Serper is not SerpAPI.** They are two different services with similar names.
> This app needs a key from **serper.dev**, which is about 40 characters long.
> A key from serpapi.com (about 64 characters) will be rejected with `403 Forbidden`.

---

## 4. Download the project

**Option A: with Git**

```bash
git clone https://github.com/Fouzia25/Multi-Agent-Customer-Support-.git
cd Multi-Agent-Customer-Support-
```

**Option B: without Git**

1. Open the GitHub page, click the green **Code** button, then **Download ZIP**.
2. Unzip it, then open a terminal inside the unzipped folder.

> Every command from here on must be run **inside the project folder**.

---

## 5. Create a virtual environment

A virtual environment (`venv`) is a private folder of Python packages for this project only,
so it won't interfere with other Python projects on your computer.

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt / cmd)**

```bat
py -3.13 -m venv venv
venv\Scripts\activate.bat
```

✅ When it's active, your terminal prompt starts with `(venv)`.

> On Windows, if PowerShell says *"running scripts is disabled on this system"*, run this once,
> then try activating again:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

## 6. Install the dependencies

With the virtual environment active:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs CrewAI, CrewAI Tools and Streamlit, and can take a few minutes.

✅ Check that it worked:

```bash
pip show crewai crewai-tools streamlit
```

You should see a version number for each of the three packages.

---

## 7. Set your API keys

The app reads its keys from **environment variables**:

| Variable | Required | What it is |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Your OpenAI key (`sk-...`) |
| `SERPER_API_KEY` | Yes | Your Serper key from serper.dev |
| `OPENAI_MODEL_NAME` | No | The OpenAI model to use. Defaults to `gpt-4o-mini`. |

Pick **one** of the two methods below.

### Method 1: type them directly into the terminal (quickest)

Replace the example values with your real keys.

**macOS / Linux**

```bash
export OPENAI_API_KEY="sk-your-openai-key"
export SERPER_API_KEY="your-serper-key"
export OPENAI_MODEL_NAME="gpt-4o-mini"   # optional
```

**Windows (PowerShell)**

```powershell
$env:OPENAI_API_KEY="sk-your-openai-key"
$env:SERPER_API_KEY="your-serper-key"
$env:OPENAI_MODEL_NAME="gpt-4o-mini"   # optional
```

**Windows (Command Prompt / cmd)**, with no quotes:

```bat
set OPENAI_API_KEY=sk-your-openai-key
set SERPER_API_KEY=your-serper-key
set OPENAI_MODEL_NAME=gpt-4o-mini
```

> These variables only last until you close that terminal window. You'll need to set them again next time.

### Method 2: save them in a `.env` file (so you don't retype them)

1. Make a copy of `.env.example` and name it `.env`:
   - macOS/Linux: `cp .env.example .env`
   - Windows: `copy .env.example .env`
2. Open `.env` in a text editor and fill in your keys, with no spaces or quotes:
   ```
   OPENAI_API_KEY=sk-your-openai-key
   SERPER_API_KEY=your-serper-key
   OPENAI_MODEL_NAME=gpt-4o-mini
   ```
3. Save the file. `.env` is listed in `.gitignore`, so Git will never upload it.
4. The app does **not** read `.env` by itself. Load it into the terminal before each run:

   **macOS / Linux**
   ```bash
   set -a; source .env; set +a
   ```

   **Windows (PowerShell)**
   ```powershell
   Get-Content .env | Where-Object { $_ -match '^\w+=' } | ForEach-Object { $k, $v = $_ -split '=', 2; Set-Item "env:$k" $v }
   ```

---

## 8. Run the app

In the same terminal (venv active, keys set):

```bash
streamlit run app.py
```

Your browser should open automatically at **<http://localhost:8501>**.
If it doesn't, copy that address into your browser.

> The first time, Streamlit may ask for your email address. Just press **Enter** to skip.

To **stop** the app, go back to the terminal and press **Ctrl + C**.

---

## 9. Use the app

1. Type a customer question in the text box, e.g. *"How do I reset a forgotten Gmail password?"*
2. Click **Submit**.
3. Watch the progress box. It updates as each agent finishes:
   - *Assistant is answering...*
   - *Searching the web...*
   - *Saving to answers.txt...*

   A full run usually takes 20–60 seconds.
4. When it's done you'll see:
   - **Assistant Answer** (left) and **Web Search Answer** (right, with sources)
   - A green message confirming the entry was saved
   - A **Download answers.txt** button

Each question is **added** to the end of `answers.txt` in the project folder, so earlier entries are kept.
An entry looks like this:

```
Timestamp: 2026-10-27 12:20:23
Query: How do I reset a forgotten Gmail password?

Answer 1 (Assistant):
...

Answer 2 (Web Search Assistant):
...
================================================================================
```

---

## 10. Running it again later

Open a terminal in the project folder, then:

**macOS / Linux**

```bash
source venv/bin/activate
set -a; source .env; set +a        # or export the keys by hand (step 7)
streamlit run app.py
```

**Windows (PowerShell)**

```powershell
.\venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -match '^\w+=' } | ForEach-Object { $k, $v = $_ -split '=', 2; Set-Item "env:$k" $v }
streamlit run app.py
```

You don't need to create the venv or install packages again.

---

## 11. Troubleshooting

| Problem | Cause and fix |
|---|---|
| The page shows **"Missing required environment variable(s)"** | The keys aren't set in the terminal that started the app. Stop the app (Ctrl + C), set the keys (step 7), then run `streamlit run app.py` again in the **same** terminal. |
| `pip install` fails with **numpy** / "Unknown compiler" / "metadata-generation-failed" | You're on Python 3.14. Delete the `venv` folder, then recreate it with Python 3.13 (step 5): `py -3.13 -m venv venv` |
| `403 Client Error: Forbidden ... serper.dev` in the terminal | Your search key is wrong, or it's a **SerpAPI** key rather than a **Serper** key. Get a key from serper.dev (step 3.2). |
| Web Search Answer says web search failed | Same as above, or your Serper credits have run out. Check your serper.dev dashboard. |
| Red error box mentioning **401**, **AuthenticationError** or "invalid api key" | Your OpenAI key is wrong or has been revoked. Create a new one. |
| Error mentioning **429**, **RateLimitError** or "insufficient_quota" | Your OpenAI account has no credits or hit its rate limit. Check billing at platform.openai.com. |
| `streamlit: command not found` / `'streamlit' is not recognized` | The venv isn't active. Activate it (step 5) and try again. |
| PowerShell: "running scripts is disabled" | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once. |
| "Port 8501 is already in use" | The app is already running in another terminal. Close it, or run `streamlit run app.py --server.port 8502`. |

---

## 12. Project structure

```
Multi-Agent-Customer-Support-/
├── app.py            # The whole app: config, tools, agents, tasks, crew and UI
├── requirements.txt  # Python packages to install
├── .env.example      # Template for your API keys (copy it to .env)
├── .gitignore        # Keeps venv/, .env, answers.txt and __pycache__/ out of Git
├── README.md         # This guide
├── .env              # Your real keys (you create this; never uploaded)
├── venv/             # Virtual environment (you create this; never uploaded)
└── answers.txt       # Log of all questions and answers (created on first run)
```
