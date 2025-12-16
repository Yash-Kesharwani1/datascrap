import os
import sys
import json
import subprocess
import requests
import re

# ==========================
# CONFIG
# ==========================
OPENROUTER_API_KEY = "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"
MODEL = "openai/open-4o-mini"

OUTPUT_FILE = "rag_output.json"


# ==========================
# TRANSCRIPT (yt-dlp)
# ==========================
def clean_vtt(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if (
            not line
            or line.startswith("WEBVTT")
            or "-->" in line
            or re.match(r"^\d+$", line)
        ):
            continue
        lines.append(line)
    return " ".join(lines)


def get_transcript_yt_dlp(video_url: str) -> str:
    print("📥 Fetching transcript using yt-dlp...")

    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--skip-download",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--sub-format", "vtt",
        video_url
    ]

    subprocess.run(cmd, check=True)

    for file in os.listdir("."):
        if file.endswith(".vtt"):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            os.remove(file)
            return clean_vtt(content)

    raise RuntimeError("❌ Transcript not found")


# ==========================
# OPENROUTER LLM CALL
# ==========================
def extract_questions_from_transcript(transcript: str, video_url: str):
    prompt = f"""
You are an AI system preparing data for a RAG-based technical interview agent.

TASK:
1. Infer JOB ROLE, PRIMARY LANGUAGE, TECHNOLOGIES, EXPERIENCE RANGE, DIFFICULTY from transcript
2. Extract ONLY technical interview questions
3. Ignore introductions, HR, casual talk
4. Generate ONE JSON OBJECT PER QUESTION

TRANSCRIPT:
\"\"\"{transcript}\"\"\"

OUTPUT RULES:
- Output ONLY valid JSON
- Output MUST be a JSON array
- No markdown, no explanation

SCHEMA:
{{
  "doc_type": "interview_question",
  "job_role": "",
  "primary_language": "",
  "technologies": [],
  "experience_range": {{
    "min_years": "0",
    "max_years": "0"
  }},
  "difficulty": "",
  "question": {{
    "text": "",
    "intent": ""
  }},
  "ideal_answer": {{
    "summary": "",
    "detailed_answer": ""
  }},
  "key_concepts": [],
  "follow_up_questions": [],
  "evaluation_criteria": {{
    "must_mention": [],
    "strong_answer_signals": [],
    "red_flags": []
  }},
  "source": {{
    "type": "YouTube Interview",
    "link": "{video_url}"
  }}
}}
"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Interview RAG Builder"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a strict JSON generator."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
    )

    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


# ==========================
# MAIN PIPELINE
# ==========================
def youtube_to_rag(youtube_url: str):
    transcript = get_transcript_yt_dlp(youtube_url)
    rag_docs = extract_questions_from_transcript(transcript, youtube_url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(rag_docs, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted {len(rag_docs)} interview questions")
    print(f"📁 Saved to {OUTPUT_FILE}")


# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        raise RuntimeError("❌ OPENROUTER_API_KEY not set")

    url = input("Enter YouTube interview URL: ").strip()
    youtube_to_rag(url)
