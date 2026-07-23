from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY was not found. Add it to the .env file."
        )

    return Groq(api_key=api_key)


def generate_candidate_explanation(
    job_description: str,
    resume_text: str,
    candidate_name: str,
    matched_skills: list[str],
    missing_skills: list[str],
    final_score: float,
) -> str:
    client = get_groq_client()

    prompt = f"""
You are a factual AI resume screening assistant.

Evaluate the candidate against the supplied job description.

Candidate:
{candidate_name}

Final score:
{final_score}/100

Matched skills:
{", ".join(matched_skills) if matched_skills else "None detected"}

Missing or unverified skills:
{", ".join(missing_skills) if missing_skills else "None detected"}

JOB DESCRIPTION:
{job_description[:6000]}

RESUME:
{resume_text[:8000]}

Return exactly these sections:

Strengths:
Write one or two concise sentences.

Gaps:
Write one or two concise sentences.

Recommendation:
Use one of these labels:
Strong Interview Recommendation
Consider for Interview
Needs Human Review
Not Recommended

Then add one concise explanation.

Rules:
- Use only information provided above.
- Do not invent skills, education, or experience.
- Treat missing information as unverified.
- Keep the complete answer below 140 words.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful recruitment assistant. "
                    "Never fabricate candidate information."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    if not content:
        return "No AI explanation was returned."

    return content.strip()