from __future__ import annotations

import html
import io
import json

import pandas as pd
import streamlit as st

from src.llm import generate_candidate_explanation
from src.parser import extract_text
from src.scorer import CandidateResult, score_candidates


st.set_page_config(
    page_title="Resume Screening AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f5f7fb;
        }

        .main .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero-container {
            background: linear-gradient(135deg, #172554 0%, #2563eb 100%);
            padding: 32px;
            border-radius: 20px;
            margin-bottom: 26px;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.20);
        }

        .hero-title {
            color: white;
            font-size: 38px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            color: #dbeafe;
            font-size: 16px;
            line-height: 1.7;
            max-width: 850px;
        }

        .section-title {
            font-size: 23px;
            font-weight: 750;
            color: #172554;
            margin-top: 12px;
            margin-bottom: 14px;
        }

        .kpi-card {
            background: white;
            padding: 22px;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.07);
            min-height: 132px;
        }

        .kpi-icon {
            font-size: 26px;
            margin-bottom: 8px;
        }

        .kpi-label {
            color: #64748b;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .kpi-value {
            color: #0f172a;
            font-size: 30px;
            font-weight: 800;
        }

        .kpi-caption {
            color: #94a3b8;
            font-size: 12px;
            margin-top: 3px;
        }

        .candidate-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #dbeafe;
            padding: 18px 20px;
            border-radius: 14px;
            margin-bottom: 15px;
        }

        .candidate-name {
            color: #172554;
            font-size: 20px;
            font-weight: 750;
        }

        .candidate-file {
            color: #64748b;
            font-size: 13px;
            margin-top: 3px;
        }

        .score-badge {
            background: #2563eb;
            color: white;
            padding: 8px 14px;
            border-radius: 30px;
            font-size: 16px;
            font-weight: 700;
        }

        .skill-box {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 18px;
            min-height: 145px;
        }

        .skill-title {
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 12px;
        }

        .skill-tags-container {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            align-items: flex-start;
        }

        .empty-skill-message {
            color: #64748b;
            font-size: 13px;
            padding-top: 4px;
        }

        .skill-tag-success {
            display: inline-block;
            background: #dcfce7;
            color: #166534;
            padding: 5px 10px;
            margin: 0;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }

        .skill-tag-warning {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 5px 10px;
            margin: 0;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }

        .reasoning-box {
            background: #f8fafc;
            border-left: 5px solid #2563eb;
            padding: 18px 20px;
            border-radius: 10px;
            color: #334155;
            line-height: 1.7;
            margin-top: 15px;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5e7eb;
            padding: 15px;
            border-radius: 13px;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
        }

        div[data-testid="stFileUploader"] {
            background: white;
            border-radius: 14px;
            padding: 8px;
        }

        div[data-testid="stExpander"] {
            background: white;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        }

        div.stButton > button {
            border-radius: 10px;
            font-weight: 700;
            min-height: 48px;
        }

        div.stDownloadButton > button {
            border-radius: 10px;
            font-weight: 650;
            min-height: 46px;
        }

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
        }

        .sidebar-logo {
            text-align: center;
            font-size: 48px;
            margin-bottom: 5px;
        }

        .sidebar-title {
            text-align: center;
            color: #172554;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 20px;
        }

        .weight-row {
            display: flex;
            justify-content: space-between;
            padding: 9px 0;
            border-bottom: 1px solid #e5e7eb;
            color: #334155;
            font-size: 14px;
        }

        .weight-value {
            color: #2563eb;
            font-weight: 750;
        }

        .footer-text {
            text-align: center;
            color: #94a3b8;
            font-size: 12px;
            margin-top: 35px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def create_results_dataframe(
    results: list[CandidateResult],
) -> pd.DataFrame:
    rows = []

    for candidate in results:
        rows.append(
            {
                "Rank": candidate.rank,
                "Candidate": candidate.candidate_name,
                "Filename": candidate.filename,
                "Final Score": candidate.final_score,
                "Semantic Score": candidate.semantic_score,
                "Skill Match Score": candidate.skill_match_score,
                "Experience Score": candidate.experience_score,
                "Education Score": candidate.education_score,
                "Matched Skills": ", ".join(candidate.matched_skills),
                "Missing Skills": ", ".join(candidate.missing_skills),
                "AI Reasoning": candidate.reasoning,
            }
        )

    return pd.DataFrame(rows)


def convert_results_to_json(
    results: list[CandidateResult],
) -> str:
    data = [result.to_dict() for result in results]

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )


def get_rank_icon(rank: int) -> str:
    icons = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    return icons.get(rank, "👤")


def render_kpi_card(
    icon: str,
    label: str,
    value: str,
    caption: str,
) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(value)}</div>
            <div class="kpi-caption">{html.escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_tags(
    skills: list[str],
    tag_type: str,
    empty_message: str,
) -> None:
    if not skills:
        st.caption(empty_message)
        return

    css_class = (
        "skill-tag-success"
        if tag_type == "success"
        else "skill-tag-warning"
    )

    tags = "".join(
        f'<span class="{css_class}">{html.escape(skill)}</span>'
        for skill in skills
    )

    st.markdown(tags, unsafe_allow_html=True)


def display_candidate(
    candidate: CandidateResult,
) -> None:
    rank_icon = get_rank_icon(candidate.rank)

    with st.expander(
        f"{rank_icon} Rank #{candidate.rank} — "
        f"{candidate.candidate_name} — "
        f"{candidate.final_score:.2f}%",
        expanded=candidate.rank == 1,
    ):
        safe_name = html.escape(candidate.candidate_name)
        safe_filename = html.escape(candidate.filename)

        st.markdown(
            f"""
<div class="candidate-header">
    <div>
        <div class="candidate-name">{rank_icon} {safe_name}</div>
        <div class="candidate-file">Source: {safe_filename}</div>
    </div>
    <div class="score-badge">{candidate.final_score:.2f}%</div>
</div>
""",
            unsafe_allow_html=True,
        )

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        metric_col1.metric(
            "Final Score",
            f"{candidate.final_score:.2f}%",
        )

        metric_col2.metric(
            "Semantic Similarity",
            f"{candidate.semantic_score:.2f}%",
        )

        metric_col3.metric(
            "Skill Match",
            f"{candidate.skill_match_score:.2f}%",
        )

        metric_col4.metric(
            "Experience",
            f"{candidate.experience_score:.2f}%",
        )

        st.markdown("##### Overall candidate suitability")

        st.progress(
            min(
                max(candidate.final_score / 100, 0.0),
                1.0,
            )
        )

        skill_col1, skill_col2 = st.columns(2)

        matched_tags = (
            "".join(
                f'<span class="skill-tag-success">{html.escape(skill)}</span>'
                for skill in candidate.matched_skills
            )
            if candidate.matched_skills
            else '<div class="empty-skill-message">No predefined matched skills detected.</div>'
        )

        missing_tags = (
            "".join(
                f'<span class="skill-tag-warning">{html.escape(skill)}</span>'
                for skill in candidate.missing_skills
            )
            if candidate.missing_skills
            else '<div class="empty-skill-message">No missing predefined skills detected.</div>'
        )

        with skill_col1:
            st.markdown(
                f"""
                <div class="skill-box">
                    <div class="skill-title">✅ Matched skills</div>
                    <div class="skill-tags-container">
                        {matched_tags}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with skill_col2:
            st.markdown(
                f"""
                <div class="skill-box">
                    <div class="skill-title">⚠️ Missing or unverified skills</div>
                    <div class="skill-tags-container">
                        {missing_tags}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 🤖 AI candidate evaluation")

        safe_reasoning = html.escape(
            candidate.reasoning
            or "AI explanation was not generated."
        ).replace("\n", "<br>")

        st.markdown(
            f"""
            <div class="reasoning-box">
                {safe_reasoning}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">🧠</div>
        <div class="sidebar-title">
            Resume Screening AI
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Scoring weights")

    st.markdown(
        """
        <div class="weight-row">
            <span>Semantic similarity</span>
            <span class="weight-value">50%</span>
        </div>

        <div class="weight-row">
            <span>Skill alignment</span>
            <span class="weight-value">30%</span>
        </div>

        <div class="weight-row">
            <span>Experience</span>
            <span class="weight-value">10%</span>
        </div>

        <div class="weight-row">
            <span>Education</span>
            <span class="weight-value">10%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Supported formats")

    st.write("📄 PDF")
    st.write("📝 DOCX")
    st.write("📃 TXT")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
<div class="hero-container">
    <div class="hero-title">AI Resume Screening Agent</div>
    <div class="hero-subtitle">
        Compare multiple resumes against a job description using
        semantic similarity, skill matching, experience analysis,
        education relevance and Groq-powered candidate explanations.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">1. Add screening information</div>',
    unsafe_allow_html=True,
)

input_col1, input_col2 = st.columns([1.35, 1])

with input_col1:
    job_description = st.text_area(
        "Job description",
        height=290,
        placeholder=(
            "Paste the complete job description here...\n\n"
            "Example:\n"
            "We are looking for a Python developer with experience in "
            "SQL, machine learning, REST APIs, Git and cloud platforms."
        ),
    )

with input_col2:
    uploaded_resumes = st.file_uploader(
        "Upload candidate resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help=(
            "Upload PDF, DOCX, or TXT resumes. "
            "The application supports 10 or more files."
        ),
    )

    generate_ai_reasoning = st.checkbox(
        "Generate Groq AI explanations",
        value=True,
        help=(
            "Generate strengths, gaps and a recommendation for every "
            "candidate using the Groq API."
        ),
    )

    if uploaded_resumes:
        st.success(
            f"{len(uploaded_resumes)} resume(s) selected."
        )

analyze_button = st.button(
    "🚀 Analyze and rank candidates",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

if analyze_button:
    if not job_description.strip():
        st.error("Please enter a job description.")
        st.stop()

    if not uploaded_resumes:
        st.error("Please upload at least one resume.")
        st.stop()

    parsed_resumes: list[dict[str, str]] = []
    parsing_errors: list[str] = []

    with st.spinner("Reading and extracting resume content..."):
        for uploaded_file in uploaded_resumes:
            try:
                file_bytes = uploaded_file.getvalue()
                file_object = io.BytesIO(file_bytes)

                resume_text = extract_text(
                    file_object,
                    uploaded_file.name,
                )

                if not resume_text.strip():
                    raise ValueError(
                        "No readable text was found in the resume."
                    )

                parsed_resumes.append(
                    {
                        "filename": uploaded_file.name,
                        "text": resume_text,
                    }
                )

            except Exception as exc:
                parsing_errors.append(
                    f"{uploaded_file.name}: {exc}"
                )

    if parsing_errors:
        st.warning(
            "Some files could not be processed:\n\n"
            + "\n\n".join(parsing_errors)
        )

    if not parsed_resumes:
        st.error("No readable resumes were found.")
        st.stop()

    with st.spinner(
        "Calculating semantic similarity and candidate scores..."
    ):
        results = score_candidates(
            job_description,
            parsed_resumes,
        )

    resume_lookup = {
        resume["filename"]: resume["text"]
        for resume in parsed_resumes
    }

    if generate_ai_reasoning:
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_candidates = len(results)

        for index, candidate in enumerate(
            results,
            start=1,
        ):
            status_text.write(
                f"Generating AI explanation for "
                f"{candidate.candidate_name}..."
            )

            try:
                candidate.reasoning = generate_candidate_explanation(
                    job_description=job_description,
                    resume_text=resume_lookup[candidate.filename],
                    candidate_name=candidate.candidate_name,
                    matched_skills=candidate.matched_skills,
                    missing_skills=candidate.missing_skills,
                    final_score=candidate.final_score,
                )

            except Exception as exc:
                candidate.reasoning = (
                    "AI explanation could not be generated. "
                    f"Error: {exc}"
                )

            progress_bar.progress(
                index / total_candidates
            )

        status_text.empty()
        progress_bar.empty()

    st.session_state["results"] = results


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

if "results" in st.session_state:
    results: list[CandidateResult] = st.session_state["results"]

    if results:
        dataframe = create_results_dataframe(results)

        top_candidate = results[0]
        average_score = dataframe["Final Score"].mean()

        shortlist_threshold = 60
        shortlisted_candidates = sum(
            candidate.final_score >= shortlist_threshold
            for candidate in results
        )

        st.markdown(
            '<div class="section-title">2. Screening overview</div>',
            unsafe_allow_html=True,
        )

        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

        with kpi_col1:
            render_kpi_card(
                icon="👥",
                label="Candidates analyzed",
                value=str(len(results)),
                caption="Successfully processed resumes",
            )

        with kpi_col2:
            render_kpi_card(
                icon="🏆",
                label="Top candidate",
                value=f"{top_candidate.final_score:.1f}%",
                caption=top_candidate.candidate_name,
            )

        with kpi_col3:
            render_kpi_card(
                icon="📊",
                label="Average score",
                value=f"{average_score:.1f}%",
                caption="Across all candidates",
            )

        with kpi_col4:
            render_kpi_card(
                icon="✅",
                label="Shortlisted",
                value=str(shortlisted_candidates),
                caption=f"Candidates scoring at least {shortlist_threshold}%",
            )

        st.markdown("")
        st.success(
            f"Successfully ranked {len(results)} candidate(s)."
        )

        ranking_tab, chart_tab, details_tab, export_tab = st.tabs(
            [
                "🏅 Candidate ranking",
                "📊 Score comparison",
                "👤 Detailed evaluations",
                "⬇️ Export results",
            ]
        )

        with ranking_tab:
            ranking_dataframe = dataframe[
                [
                    "Rank",
                    "Candidate",
                    "Final Score",
                    "Semantic Score",
                    "Skill Match Score",
                    "Experience Score",
                    "Education Score",
                ]
            ].copy()

            ranking_dataframe["Rank"] = ranking_dataframe["Rank"].apply(
                lambda rank: (
                    f"{get_rank_icon(rank)} #{rank}"
                )
            )

            st.dataframe(
                ranking_dataframe,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.TextColumn(
                        "Rank",
                        width="small",
                    ),
                    "Candidate": st.column_config.TextColumn(
                        "Candidate",
                        width="medium",
                    ),
                    "Final Score": st.column_config.ProgressColumn(
                        "Final Score",
                        min_value=0,
                        max_value=100,
                        format="%.2f%%",
                    ),
                    "Semantic Score": st.column_config.ProgressColumn(
                        "Semantic",
                        min_value=0,
                        max_value=100,
                        format="%.2f%%",
                    ),
                    "Skill Match Score": st.column_config.ProgressColumn(
                        "Skill Match",
                        min_value=0,
                        max_value=100,
                        format="%.2f%%",
                    ),
                    "Experience Score": st.column_config.NumberColumn(
                        "Experience",
                        format="%.2f%%",
                    ),
                    "Education Score": st.column_config.NumberColumn(
                        "Education",
                        format="%.2f%%",
                    ),
                },
            )

        
        with chart_tab:
            chart_data = dataframe.set_index("Candidate")[
                [
                    "Final Score",
                    "Semantic Score",
                    "Skill Match Score",
                ]
            ]

            st.bar_chart(
                chart_data,
                use_container_width=True,
            )

        with details_tab:
            for candidate in results:
                display_candidate(candidate)

        with export_tab:
            st.markdown("### Download complete screening results")

            st.write(
                "Export the candidate ranking, score breakdown, skill "
                "analysis and AI explanation."
            )

            csv_data = dataframe.to_csv(
                index=False
            ).encode("utf-8")

            json_data = convert_results_to_json(results)

            download_column1, download_column2 = st.columns(2)

            with download_column1:
                st.download_button(
                    label="📥 Download ranked CSV",
                    data=csv_data,
                    file_name="ranked_candidates.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with download_column2:
                st.download_button(
                    label="📥 Download ranked JSON",
                    data=json_data,
                    file_name="ranked_candidates.json",
                    mime="application/json",
                    use_container_width=True,
                )

            st.info(
                "CSV is suitable for Excel and spreadsheet analysis. "
                "JSON is suitable for APIs and software integration."
            )