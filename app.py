from modules.notion_tasks import create_notion_task
from modules.memory import create_tables, save_decision, get_previous_decisions
import streamlit as st
import os
from dotenv import load_dotenv
from modules.meeting_analyzer import analyze_meeting, detect_conflicts

load_dotenv()
create_tables()

st.set_page_config(
    page_title="MEETMIND AI",
    page_icon="🧠",
    layout="wide")

st.title("🧠 MEETMIND AI")
st.subheader("From meeting conversations to actual implementation.")

st.write("An AI-powered meeting assistant that remembers decisions, ""detects conflicts and converts actions into tasks.")

gemini_ready = bool(os.getenv("GEMINI_API_KEY"))
notion_ready = bool(os.getenv("NOTION_TOKEN"))
database_ready = bool(os.getenv("NOTION_DATABASE_ID"))

st.sidebar.header("System Status")
st.sidebar.write(
    "Gemini AI: " + ("🟢 Configured" if gemini_ready else "🔴 Missing"))
st.sidebar.write(
    "Notion: " + ("🟢 Configured" if notion_ready else "🔴 Missing"))
st.sidebar.write("Notion Database: " +
                 ("🟢 Configured" if database_ready else "🔴 Missing"))

st.header("📄 Meeting Transcript")
meeting_title = st.text_input(
    "Meeting Title", placeholder="e.g. Website Launch Planning")

uploaded_file = st.file_uploader(
    "Upload your meeting transcript", type=["txt"])
transcript = ""
if uploaded_file is not None:
    transcript = uploaded_file.read().decode("utf-8")
else:
    transcript = st.text_area("Or paste your meeting transcript here",
                              height=350, placeholder="Paste your meeting conversation...")

if st.button("Analyse Meeting", type="primary"):

    if transcript.strip():

        try:
            with st.spinner("Analysing meeting..."):
                result = analyze_meeting(transcript)

                previous_decisions = get_previous_decisions()

                conflicts = detect_conflicts(
                    result["decisions"],
                    previous_decisions
                )

            st.success("Analysis complete!")

            st.subheader("👥 Speakers")
            st.write(result["speakers"])

            st.subheader("✅ Decisions")
            for decision in result["decisions"]:
                st.write(
                    f"{decision['decision']} — {decision['speaker']}"
                )

            st.subheader("⚠️ Conflict Detection")
            if conflicts:
                for conflict in conflicts:
                    st.error(
                        f"New: {conflict['new_decision']}\n\n"
                        f"Previous: {conflict['previous_decision']}\n\n"
                        f"Meeting: {conflict['previous_meeting']}\n\n"
                        f"Reason: {conflict['explanation']}"
                    )
            else:
                st.success("No potential conflicts detected.")

            st.subheader("🧠 Meeting Memory")
            if previous_decisions:
                for decision in previous_decisions:
                    st.info(
                        f"{decision[2]}: {decision[0]} "
                        f"(Speaker: {decision[1]})"
                    )
            else:
                st.write("No previous decisions stored yet.")

            st.subheader("📋 Action Items")
            st.dataframe(result["tasks"])

            st.subheader("🚀 Approve Tasks")

            approved = st.checkbox(
                "I approve sending these tasks to Notion."
            )

            if st.button("Create Approved Tasks"):
                if approved:
                    for task in result["tasks"]:
                        try:
                            deadline = task["deadline"]

                            if deadline == "Unknown" or len(deadline) != 10:
                                deadline = None

                            priority = task["priority"]
                            if priority == "Unknown":
                                priority = "Medium"

                            create_notion_task(
                                task["task"],
                                task["owner"],
                                deadline,
                                priority,
                                meeting_title or "Untitled Meeting"
                            )

                            st.success(
                                f"Created: {task['task']}"
                            )

                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("Approve the tasks first.")

            # Save decisions after displaying previous memory
            for decision in result["decisions"]:
                save_decision(
                    decision["decision"],
                    decision["speaker"],
                    meeting_title or "Untitled Meeting"
                )

        except Exception as e:
            st.error(f"Analysis failed: {e}")

    else:
        st.warning("Please upload or paste a meeting transcript.")