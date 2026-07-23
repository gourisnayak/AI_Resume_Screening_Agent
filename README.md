# 🤖 AI Resume Screening Agent

An AI-powered resume screening application that automatically evaluates and ranks multiple candidate resumes against a job description using semantic similarity, skill matching, experience analysis, education relevance and AI-generated explanations.

Developed as part of the **Rooman Technologies 24-Hour AI Agent Challenge**, this project helps recruiters streamline the initial candidate screening process by combining deterministic scoring with Large Language Model (LLM) insights.

---

## 📌 Project Overview

Traditional resume screening is time-consuming and subjective. This application automates the first stage of recruitment by analyzing resumes and comparing them against a given job description.

The system:

- Accepts a job description
- Parses multiple resumes (PDF, DOCX, TXT)
- Extracts relevant information
- Computes multiple evaluation scores
- Ranks candidates automatically
- Generates AI-powered strengths and gap analysis
- Exports results as CSV and JSON

The final ranking is based on a weighted scoring system, while the LLM provides human-readable explanations without affecting the numerical score.

---

# ✨ Features

## Resume Processing

- Upload multiple resumes simultaneously
- Supports PDF, DOCX, and TXT formats
- Automatic resume parsing and text extraction
- Handles batches of 10+ resumes efficiently

## Intelligent Candidate Evaluation

- Semantic similarity matching between resume and job description
- Skill extraction and comparison
- Experience relevance evaluation
- Education relevance evaluation
- Weighted final candidate score
- Automatic candidate ranking

## AI-Assisted Analysis

- AI-generated candidate summaries
- Strengths identification
- Missing or unverified skills detection
- Recruiter-friendly explanations using Groq LLM

## Export Support

- Download ranked candidates as CSV
- Download ranked candidates as JSON

## User Interface

- Modern Streamlit interface
- Interactive score cards
- Candidate-wise expandable reports
- Visual skill tags
- Download buttons for results

---

# 🏗️ System Architecture

The application follows a modular pipeline:

1. **Job Description Input**
   - Recruiter provides the job description.

2. **Resume Parser**
   - Extracts text from PDF, DOCX, and TXT resumes.

3. **Information Extraction**
   - Identifies skills, education, and experience.

4. **Scoring Engine**
   - Computes:
     - Semantic Similarity (50%)
     - Skill Match (30%)
     - Experience (10%)
     - Education (10%)

5. **LLM Analysis**
   - Groq generates candidate strengths, gaps, and recommendations.

6. **Ranking & Export**
   - Candidates are ranked and exported as CSV and JSON.

7. **Streamlit Dashboard**
   - Displays rankings, detailed reports, and download options.

### Workflow

1. The recruiter enters a job description.
2. Multiple resumes are uploaded.
3. The parser extracts text from each resume.
4. Skills, education, and experience are identified.
5. Each resume is scored using the weighted evaluation model.
6. Candidates are ranked based on the final score.
7. Groq generates recruiter-friendly explanations.
8. Results are displayed in the Streamlit dashboard and exported as CSV or JSON.

   ---

# 🛠️ Tech Stack

The project is built using the following technologies:

- **Python** – Core programming language
- **Streamlit** – Interactive web interface
- **Groq API** – AI-generated candidate analysis
- **Sentence Transformers** – Semantic similarity between resumes and job descriptions
- **PyPDF2 & python-docx** – Resume parsing
- **Pandas** – Data processing and result generation
- **python-dotenv** – Environment variable management
- **CSV & JSON** – Exporting ranked candidate data

   ---

## 📁 Project Structure

ResumeScreeningAI/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── src/
│   ├── parser.py
│   ├── scorer.py
│   ├── skills.py
│   ├── llm.py
│   └── __init__.py
│
├── data/
│   ├── job_descriptions/
│   └── resumes/
│
└── outputs/

   ---