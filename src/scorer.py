from __future__ import annotations

import re
from dataclasses import asdict, dataclass

import streamlit as st

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.skills import calculate_skill_match


MODEL_NAME = "all-MiniLM-L6-v2"


@dataclass
class CandidateResult:
    rank: int
    candidate_name: str
    filename: str
    semantic_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    final_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reasoning: str

    def to_dict(self) -> dict:
        return asdict(self)


def extract_candidate_name(text: str, filename: str) -> str:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:5]:
        if (
            2 <= len(line.split()) <= 5
            and len(line) <= 60
            and not any(char.isdigit() for char in line)
            and "resume" not in line.lower()
            and "curriculum vitae" not in line.lower()
        ):
            return line.title()

    return filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()


def extract_experience_years(text: str) -> float:
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?experience",
        r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)",
    ]

    values: list[float] = []

    for pattern in patterns:
        matches = re.findall(pattern, text.lower())

        for match in matches:
            try:
                values.append(float(match))
            except ValueError:
                continue

    return max(values, default=0.0)


def calculate_experience_score(text: str) -> float:
    years = extract_experience_years(text)

    if years >= 5:
        return 100.0
    if years >= 3:
        return 85.0
    if years >= 2:
        return 70.0
    if years >= 1:
        return 55.0

    internship_terms = [
        "internship",
        "intern",
        "trainee",
        "apprentice",
    ]

    if any(term in text.lower() for term in internship_terms):
        return 40.0

    return 20.0


def calculate_education_score(text: str) -> float:
    normalized = text.lower()

    if any(
        term in normalized
        for term in [
            "phd",
            "doctor of philosophy",
        ]
    ):
        return 100.0

    if any(
        term in normalized
        for term in [
            "master",
            "m.tech",
            "mtech",
            "m.sc",
            "msc",
            "mba",
            "mca",
        ]
    ):
        return 90.0

    if any(
        term in normalized
        for term in [
            "bachelor",
            "b.tech",
            "btech",
            "b.e",
            "bsc",
            "b.sc",
            "computer science",
            "engineering",
        ]
    ):
        return 75.0

    if any(
        term in normalized
        for term in [
            "diploma",
            "associate degree",
        ]
    ):
        return 55.0

    return 30.0

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(MODEL_NAME)

def score_candidates(
    job_description: str,
    resumes: list[dict[str, str]],
) -> list[CandidateResult]:
    model = load_embedding_model()

    resume_texts = [
        resume["text"]
        for resume in resumes
    ]

    all_texts = [job_description] + resume_texts

    embeddings = model.encode(
        all_texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    jd_embedding = embeddings[0].reshape(1, -1)
    resume_embeddings = embeddings[1:]

    similarity_values = cosine_similarity(
        jd_embedding,
        resume_embeddings,
    )[0]

    results: list[CandidateResult] = []

    for resume, similarity in zip(resumes, similarity_values):
        filename = resume["filename"]
        text = resume["text"]

        semantic_score = round(float(similarity) * 100, 2)

        skill_score, matched_skills, missing_skills = calculate_skill_match(
            job_description,
            text,
        )

        experience_score = calculate_experience_score(text)
        education_score = calculate_education_score(text)

        final_score = (
            semantic_score * 0.50
            + skill_score * 0.30
            + experience_score * 0.10
            + education_score * 0.10
        )

        results.append(
            CandidateResult(
                rank=0,
                candidate_name=extract_candidate_name(text, filename),
                filename=filename,
                semantic_score=semantic_score,
                skill_match_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
                final_score=round(final_score, 2),
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                reasoning="AI explanation not generated.",
            )
        )

    results.sort(
        key=lambda candidate: candidate.final_score,
        reverse=True,
    )

    for index, candidate in enumerate(results, start=1):
        candidate.rank = index

    return results