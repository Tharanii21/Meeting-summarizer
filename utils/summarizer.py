import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def generate_meeting_summary(transcript):
    """
    Generate a meeting summary, key decisions,
    and action items from the transcript.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=api_key)

    prompt = f"""
You are a professional meeting assistant.

Analyze the meeting transcript below.

Create an action-oriented meeting report with exactly
these three sections:

## Meeting Summary
Give a concise summary of the main topics discussed.

## Key Decisions
List the important decisions made during the meeting.
If no clear decisions are mentioned, say "No clear decisions identified."

## Action Items
List the tasks that need to be completed.
For each task, mention the responsible person and deadline
only when they are actually mentioned in the transcript.
Do not invent information.

Meeting Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a professional meeting summarization assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content