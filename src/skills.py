from __future__ import annotations

import re


SKILL_LIBRARY = {
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "react",
    "react native",
    "node.js",
    "express",
    "html",
    "css",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "natural language processing",
    "nlp",
    "computer vision",
    "data analysis",
    "data science",
    "power bi",
    "tableau",
    "excel",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "google cloud",
    "linux",
    "rest api",
    "fastapi",
    "flask",
    "django",
    "streamlit",
    "langchain",
    "llm",
    "generative ai",
    "rag",
    "prompt engineering",
    "sentence transformers",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("/", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text: str) -> list[str]:
    normalized_text = normalize_text(text)
    found_skills: list[str] = []

    for skill in SKILL_LIBRARY:
        escaped_skill = re.escape(skill)

        pattern = rf"(?<!\w){escaped_skill}(?!\w)"

        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return sorted(found_skills)


def calculate_skill_match(
    job_description: str,
    resume_text: str,
) -> tuple[float, list[str], list[str]]:
    jd_skills = set(extract_skills(job_description))
    resume_skills = set(extract_skills(resume_text))

    if not jd_skills:
        return 0.0, [], []

    matched_skills = sorted(jd_skills.intersection(resume_skills))
    missing_skills = sorted(jd_skills.difference(resume_skills))

    skill_score = len(matched_skills) / len(jd_skills) * 100

    return round(skill_score, 2), matched_skills, missing_skills