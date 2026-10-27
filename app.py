"""Multi-agent customer support app (CrewAI + Streamlit).

Sequential data flow:
    user query
      -> Task 1 (Assistant)            answers from its own knowledge
      -> Task 2 (Web Search Assistant) answers from SerperDevTool results, citing URLs
      -> Task 3 (Entry Agent)          receives answers 1 & 2 via context=[task1, task2],
                                       saves them to answers.txt, returns both answers
The UI reads answers 1 and 2 straight from CrewOutput.tasks_output[0] / [1].
"""

import os
import threading
from datetime import datetime
from pathlib import Path

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# =============================================================================
# Config / environment checks
# =============================================================================

st.set_page_config(page_title="Multi-Agent Customer Support", page_icon="🤖", layout="wide")

REQUIRED_KEYS = {
    "OPENAI_API_KEY": "https://platform.openai.com/api-keys",
    "SERPER_API_KEY": "https://serper.dev",
}
MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
ANSWERS_FILE = Path(__file__).parent / "answers.txt"

missing = [k for k in REQUIRED_KEYS if not os.environ.get(k)]
if missing:
    lines = "\n".join(f"- `{k}` (get one at {REQUIRED_KEYS[k]})" for k in missing)
    st.error(
        f"Missing required environment variable(s):\n\n{lines}\n\n"
        "Set them in the terminal you launch Streamlit from, then restart:\n\n"
        "**macOS/Linux:** `export OPENAI_API_KEY=\"sk-...\"`\n\n"
        "**Windows PowerShell:** `$env:OPENAI_API_KEY=\"sk-...\"`\n\n"
        "**Windows cmd:** `set OPENAI_API_KEY=sk-...`\n\n"
        "(Same for `SERPER_API_KEY`.) Then run `streamlit run app.py`."
    )
    st.stop()

# Import CrewAI only after the key check so a missing key gives a clean message.
from crewai import LLM, Agent, Crew, Process, Task  # noqa: E402
from crewai.tools import tool  # noqa: E402
from crewai_tools import SerperDevTool  # noqa: E402

# =============================================================================
# Tools
# =============================================================================

_file_lock = threading.Lock()


@tool("save_answers")
def save_answers(query: str, assistant_answer: str, web_answer: str) -> str:
    """Append the customer's query, the Assistant's answer (Answer 1) and the
    Web Search Assistant's answer (Answer 2) to answers.txt. Pass each answer
    in full, exactly as written by the earlier agents."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"Timestamp: {timestamp}\n"
        f"Query: {query}\n\n"
        f"Answer 1 (Assistant):\n{assistant_answer}\n\n"
        f"Answer 2 (Web Search Assistant):\n{web_answer}\n"
        f"{'=' * 80}\n\n"
    )
    with _file_lock, open(ANSWERS_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    return f"Saved entry for query '{query}' to {ANSWERS_FILE.name} at {timestamp}."


# =============================================================================
# Agents
# =============================================================================


def build_agents(llm: LLM) -> tuple[Agent, Agent, Agent]:
    # Agent 1: knowledge-only answer, deliberately no tools.
    assistant = Agent(
        role="Assistant",
        goal="Give the customer a clear, accurate and friendly answer to their question "
        "using your own knowledge.",
        backstory="You are an experienced customer support specialist who explains things "
        "simply, is honest about uncertainty, and never invents facts.",
        tools=[],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
    # Agent 2: the only agent with web search.
    web_assistant = Agent(
        role="Web Search Assistant",
        goal="Search the web for the customer's question and write an up-to-date answer "
        "grounded in the search results, citing source URLs.",
        backstory="You are a support researcher who checks current, authoritative sources "
        "before answering and always shows where information came from.",
        tools=[SerperDevTool()],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
    # Agent 3: records both answers to answers.txt.
    entry_agent = Agent(
        role="Entry Agent",
        goal="Record every customer query and both support answers in answers.txt, "
        "then report both answers back.",
        backstory="You are a meticulous support operations clerk who keeps an accurate "
        "log of every customer interaction, copying answers verbatim.",
        tools=[save_answers],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
    return assistant, web_assistant, entry_agent


# =============================================================================
# Tasks
# =============================================================================


def build_tasks(assistant: Agent, web_assistant: Agent, entry_agent: Agent, callbacks: dict) -> list[Task]:
    # {query} is filled in by crew.kickoff(inputs={"query": ...}).
    task1 = Task(
        description="A customer asked: \"{query}\"\n\n"
        "Answer it directly from your own knowledge. Do not use any tools.",
        expected_output="A helpful, well-structured answer in markdown.",
        agent=assistant,
        callback=callbacks.get("assistant"),
    )
    task2 = Task(
        description="A customer asked: \"{query}\"\n\n"
        "Search the web for this question, then write an answer grounded in the "
        "search results. Cite the source URLs you relied on. If the search tool "
        "returns an error or no results, say clearly that web search failed and "
        "do not invent sources.",
        expected_output="A markdown answer based on web results, ending with a 'Sources' "
        "list of URLs.",
        agent=web_assistant,
        callback=callbacks.get("web"),
    )
    # context=[task1, task2] passes both earlier outputs into this task's prompt.
    task3 = Task(
        description="The customer's query was: \"{query}\"\n\n"
        "You have received two answers in your context: the Assistant's answer "
        "(Answer 1) and the Web Search Assistant's answer (Answer 2). Call the "
        "save_answers tool exactly once with query=\"{query}\", "
        "assistant_answer=<Answer 1 verbatim>, web_answer=<Answer 2 verbatim>. "
        "Then return both answers.",
        expected_output="The save confirmation, followed by Answer 1 and Answer 2.",
        agent=entry_agent,
        context=[task1, task2],
        callback=callbacks.get("entry"),
    )
    return [task1, task2, task3]


# =============================================================================
# Crew builder
# =============================================================================


def build_crew(callbacks: dict) -> Crew:
    llm = LLM(model=MODEL_NAME)
    agents = build_agents(llm)
    return Crew(
        agents=list(agents),
        tasks=build_tasks(*agents, callbacks=callbacks),
        process=Process.sequential,  # Assistant -> Web Search Assistant -> Entry Agent
        verbose=True,
    )


# =============================================================================
# UI
# =============================================================================

st.title("🤖 Multi-Agent Customer Support")
st.markdown(
    f"Three AI agents (model: `{MODEL_NAME}`) handle each question **in sequence**:\n"
    "1. **Assistant** answers from its own knowledge.\n"
    "2. **Web Search Assistant** searches the web and answers with cited sources.\n"
    "3. **Entry Agent** saves the query and both answers to `answers.txt`."
)

if "results" not in st.session_state:
    st.session_state.results = None

with st.form("query_form"):
    query = st.text_area("Your question", placeholder="e.g. How do I reset my router?")
    submitted = st.form_submit_button("Submit")

if submitted:
    query = query.strip()
    if not query:
        st.warning("Please enter a question before submitting.")
    else:
        with st.status("Assistant is answering...", expanded=True) as status:
            # Task callbacks may run outside the script thread; reattach the
            # Streamlit context so they can update the status box.
            ctx = get_script_run_ctx()

            def _progress(done_msg: str, next_label: str | None):
                def _cb(_output):
                    add_script_run_ctx(threading.current_thread(), ctx)
                    status.write(done_msg)
                    if next_label:
                        status.update(label=next_label)
                return _cb

            callbacks = {
                "assistant": _progress("✅ Assistant answered.", "Searching the web..."),
                "web": _progress("✅ Web search answer ready.", "Saving to answers.txt..."),
                "entry": _progress("✅ Entry saved.", None),
            }
            try:
                result = build_crew(callbacks).kickoff(inputs={"query": query})
                outputs = result.tasks_output
                st.session_state.results = {
                    "query": query,
                    "assistant": outputs[0].raw,
                    "web": outputs[1].raw,
                }
                status.update(label="Done!", state="complete", expanded=False)
            except Exception as e:  # invalid key, network error, rate limit, ...
                status.update(label="Something went wrong", state="error")
                st.error(
                    "Sorry, the agents couldn't complete your request. Check that your "
                    "OPENAI_API_KEY and SERPER_API_KEY are valid and that you're online, "
                    f"then try again.\n\nDetails: `{type(e).__name__}: {e}`"
                )

results = st.session_state.results
if results:
    st.subheader(f"Results for: {results['query']}")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Assistant Answer")
        st.markdown(results["assistant"])
    with col2:
        st.header("Web Search Answer")
        st.markdown(results["web"])

    if ANSWERS_FILE.exists():
        st.success(f"Entry saved to `{ANSWERS_FILE.name}`.")
        st.download_button(
            "Download answers.txt",
            data=ANSWERS_FILE.read_text(encoding="utf-8"),
            file_name="answers.txt",
            mime="text/plain",
        )
    else:
        st.warning("answers.txt was not found — the Entry Agent may not have saved this entry.")
