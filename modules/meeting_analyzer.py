import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MEETING_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "speakers": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "decisions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "decision": {"type": "STRING"},
                    "speaker": {"type": "STRING"}
                },
                "required": ["decision", "speaker"]
            }
        },
        "tasks": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "task": {"type": "STRING"},
                    "owner": {"type": "STRING"},
                    "deadline": {"type": "STRING"},
                    "priority": {
                        "type": "STRING",
                        "enum": ["High", "Medium", "Low", "Unknown"]
                    }
                },
                "required": [
                    "task",
                    "owner",
                    "deadline",
                    "priority"
                ]
}}},
    "required": ["speakers", "decisions", "tasks"]}


def analyze_meeting(transcript):

    prompt = f"""
    You are MEETMIND AI, an intelligent meeting assistant.

    Analyse the following meeting transcript.

    Identify:
    1. All speakers.
    2. Explicitly agreed decisions.
    3. Action items.
    4. The person responsible for each task.
    5. Deadlines, if mentioned.

    Important rules:
    - Never invent decisions or tasks.
    - If an owner is unknown, write Unknown.
    - If a deadline is missing, write Unknown.
    - Only extract actual commitments.
    - Do not treat suggestions as confirmed decisions.

    MEETING TRANSCRIPT:

    {transcript}
    """

    response = client.models.generate_content(
       model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MEETING_SCHEMA,
            temperature=0.2))
    
    return json.loads(response.text)
def detect_conflicts(new_decisions, previous_decisions):

    if not previous_decisions:
        return []

    prompt = f"""
    You are MEETMIND AI's decision conflict detector.

    Compare the NEW decisions with the PREVIOUS decisions.

    NEW DECISIONS:
    {json.dumps(new_decisions)}

    PREVIOUS DECISIONS:
    {json.dumps(previous_decisions)}

    Identify genuine contradictions or changes in previously
    agreed decisions.

    Do not flag unrelated decisions.
    Do not assume every change is a conflict.

    Return JSON in this format:
    {{
        "conflicts": [
            {{
                "new_decision": "New decision",
                "previous_decision": "Earlier decision",
                "previous_meeting": "Meeting title",
                "explanation": "Why they conflict"
            }}]}}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1))

    return json.loads(response.text)["conflicts"]