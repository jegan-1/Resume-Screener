import streamlit as st
import pandas as pd
import plotly.express as px
import os
import tempfile
from extractor import process_resume
from scorer import rank_resumes, SKILLS_DATABASE
from database import (
    create_tables,
    save_job_search,
    save_resume_results,
    get_all_searches,
    get_search_results
)

st.set_page_config(
    page_title="ResumeIQ — Resume Screening",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
* { margin: 0; padding: 0; box-sizing: border-box; }

.stApp {
    background-color: #0a0a0f;
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0d14;
    border-right: 1px solid #1e1e2e;
}
section[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin-bottom: 0.4rem;
    display: block;
    transition: all 0.3s;
    font-size: 0.9rem;
    letter-spacing: 0.3px;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    border-color: #c9a96e;
    color: #c9a96e !important;
    background: rgba(201,169,110,0.05);
}

/* ── Gold divider ── */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        #c9a96e 30%,
        #f0d080 50%,
        #c9a96e 70%,
        transparent 100%
    );
    margin: 1.5rem 0;
}

/* ── Logo area ── */
.logo-area {
    padding: 2.5rem 0 1rem 0;
    text-align: center;
}
.logo-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: 4px;
    background: linear-gradient(135deg,
        #c9a96e 0%,
        #f0d080 40%,
        #c9a96e 60%,
        #8b6914 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    filter: drop-shadow(0 0 30px rgba(201,169,110,0.3));
}
.logo-tagline {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 6px;
    color: #666680;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #c9a96e;
    margin-bottom: 0.8rem;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #f0ece0;
    margin-bottom: 1.2rem;
    line-height: 1.3;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #0d0d14;
    border: 1px solid #1e1e2e;
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #c9a96e, #f0d080, #c9a96e);
}
div[data-testid="metric-container"]:hover {
    border-color: #c9a96e;
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4),
                0 0 30px rgba(201,169,110,0.1);
}
div[data-testid="metric-container"] [data-testid="metric-label"] {
    font-size: 0.7rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #666680 !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.8rem !important;
    color: #f0ece0 !important;
}

/* ── Primary Button ── */
.stButton > button {
    background: transparent;
    color: #c9a96e !important;
    border: 1px solid #c9a96e;
    border-radius: 2px;
    padding: 0.75rem 2.5rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 4px;
    text-transform: uppercase;
    width: 100%;
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}
.stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg,
        transparent,
        rgba(201,169,110,0.15),
        transparent
    );
    transition: left 0.5s ease;
}
.stButton > button:hover::before {
    left: 100%;
}
.stButton > button:hover {
    background: rgba(201,169,110,0.08);
    box-shadow: 0 0 30px rgba(201,169,110,0.2),
                inset 0 0 30px rgba(201,169,110,0.05);
    transform: translateY(-2px);
    letter-spacing: 6px;
}

/* ── Input fields ── */
.stTextInput input {
    background: #0d0d14 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 2px !important;
    color: #f0ece0 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.9rem !important;
    transition: all 0.3s !important;
}
.stTextInput input:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 20px rgba(201,169,110,0.1) !important;
}
.stTextInput input::placeholder {
    color: #444460 !important;
}
.stTextArea textarea {
    background: #0d0d14 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 2px !important;
    color: #f0ece0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    transition: all 0.3s !important;
}
.stTextArea textarea:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 20px rgba(201,169,110,0.1) !important;
}
.stTextArea textarea::placeholder {
    color: #444460 !important;
}

/* ── Labels ── */
.stTextInput label, .stTextArea label,
.stFileUploader label {
    font-size: 0.7rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #666680 !important;
    font-weight: 500 !important;
}

/* ── File uploader ── */
section[data-testid="stFileUploadDropzone"] {
    background: #0d0d14;
    border: 1px dashed #2a2a3e;
    border-radius: 4px;
    transition: all 0.3s;
}
section[data-testid="stFileUploadDropzone"]:hover {
    border-color: #c9a96e;
    background: rgba(201,169,110,0.03);
}

/* ── Score badges ── */
.badge {
    display: inline-block;
    padding: 0.25rem 1rem;
    border-radius: 2px;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 600;
}
.badge-gold {
    background: rgba(201,169,110,0.1);
    border: 1px solid #c9a96e;
    color: #c9a96e;
}
.badge-silver {
    background: rgba(180,180,200,0.1);
    border: 1px solid #9090a8;
    color: #9090a8;
}
.badge-bronze {
    background: rgba(180,100,80,0.1);
    border: 1px solid #b46450;
    color: #b46450;
}

/* ── Expander ── */
details {
    background: #0d0d14 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 4px !important;
    margin-bottom: 0.5rem !important;
    transition: all 0.3s !important;
}
details:hover {
    border-color: #c9a96e !important;
}
details summary {
    color: #f0ece0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px !important;
    padding: 1rem 1.2rem !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border: 1px solid #1e1e2e !important;
    border-radius: 4px !important;
}

/* ── Info / Success / Warning ── */
.stSuccess {
    background: rgba(201,169,110,0.08) !important;
    border: 1px solid rgba(201,169,110,0.3) !important;
    border-radius: 4px !important;
    color: #c9a96e !important;
}
.stInfo {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 4px !important;
}
.stWarning {
    background: rgba(180,100,80,0.08) !important;
    border: 1px solid rgba(180,100,80,0.3) !important;
    border-radius: 4px !important;
}

/* ── Sidebar step items ── */
.sidebar-step {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1a1a28;
    font-size: 0.85rem;
    color: #a0a0b8;
}
.sidebar-step-num {
    width: 24px;
    height: 24px;
    border: 1px solid #c9a96e;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    color: #c9a96e;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ── HEADER ──
st.markdown("""
<div class="logo-area">
    <div class="logo-title">RESUMEIQ</div>
    <div class="logo-tagline">Precision Candidate Intelligence</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 0 0.5rem 0;">
        <div style="font-size:0.65rem; letter-spacing:4px;
             text-transform:uppercase; color:#c9a96e;
             margin-bottom:1rem;">
            NAVIGATION
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        ["Screen Resumes", "Previous Results"]
    )

    st.markdown('<div class="gold-divider"></div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.65rem; letter-spacing:4px;
         text-transform:uppercase; color:#c9a96e;
         margin-bottom:1rem;">
        HOW IT WORKS
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Enter the job title"),
        ("02", "Paste job description"),
        ("03", "Upload PDF resumes"),
        ("04", "Click Screen button"),
        ("05", "View ranked results"),
    ]
    for num, text in steps:
        st.markdown(f"""
        <div class="sidebar-step">
            <div class="sidebar-step-num">{num}</div>
            <div>{text}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.65rem; letter-spacing:4px;
         text-transform:uppercase; color:#c9a96e;
         margin-bottom:1rem;">
        SCORING CRITERIA
    </div>
    <div style="font-size:0.82rem; color:#a0a0b8; line-height:2;">
        Skills Match &nbsp;&nbsp;&nbsp; 60 pts<br>
        Experience &nbsp;&nbsp;&nbsp;&nbsp; 25 pts<br>
        Education &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 15 pts<br>
        <span style="color:#c9a96e;">Total &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        100 pts</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.65rem; letter-spacing:4px;
         text-transform:uppercase; color:#c9a96e;
         margin-bottom:1rem;">
        MATCH LEVELS
    </div>
    <div style="font-size:0.82rem; color:#a0a0b8; line-height:2.2;">
        <span style="color:#c9a96e;">◆</span>
        Strong Match &nbsp;&nbsp; 70+<br>
        <span style="color:#9090a8;">◆</span>
        Moderate Match &nbsp; 40–69<br>
        <span style="color:#b46450;">◆</span>
        Weak Match &nbsp;&nbsp;&nbsp;&nbsp; below 40
    </div>
    """, unsafe_allow_html=True)

# ── PAGE 1 — SCREEN RESUMES ──
if page == "Screen Resumes":

    col_main, col_gap = st.columns([10, 1])
    with col_main:

        st.markdown(
            '<div class="section-label">Position Details</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="section-heading">Define the Role</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            job_title = st.text_input(
                "Job Title",
                placeholder="e.g. Senior Data Analyst"
            )
        with col2:
            st.markdown("")

        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the complete job description here...",
            height=160
        )

        st.markdown('<div class="gold-divider"></div>',
                    unsafe_allow_html=True)

        st.markdown(
            '<div class="section-label">Candidate Resumes</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="section-heading">Upload Documents</div>',
            unsafe_allow_html=True
        )

        uploaded_files = st.file_uploader(
            "PDF format — multiple files supported",
            type=['pdf'],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(
                f"{len(uploaded_files)} document(s) ready for analysis"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            screen_btn = st.button("SCREEN CANDIDATES")

        if screen_btn:
            if not job_title:
                st.error("Please enter a job title.")
            elif not job_description:
                st.error("Please enter a job description.")
            elif not uploaded_files:
                st.error("Please upload at least one resume.")
            else:
                with st.spinner("Analysing candidates..."):
                    resumes_data = []
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix='.pdf'
                        ) as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name

                        resume_data = process_resume(
                            tmp_path, SKILLS_DATABASE
                        )
                        if resume_data:
                            resume_data['file_name'] = (
                                uploaded_file.name
                            )
                            resumes_data.append(resume_data)
                        os.unlink(tmp_path)

                    if resumes_data:
                        ranked = rank_resumes(
                            resumes_data, job_description
                        )
                        search_id = save_job_search(
                            job_title, job_description
                        )
                        save_resume_results(search_id, ranked)
                        st.session_state['ranked'] = ranked
                        st.session_state['job_title'] = job_title
                        st.balloons()

        # ── RESULTS ──
        if 'ranked' in st.session_state:
            ranked = st.session_state['ranked']

            st.markdown('<div class="gold-divider"></div>',
                        unsafe_allow_html=True)

            st.markdown(
                '<div class="section-label">Analysis Complete</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="section-heading">Screening Results</div>',
                unsafe_allow_html=True
            )

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            avg = sum(
                r['total_score'] for r in ranked
            ) / len(ranked)
            with col1:
                st.metric("CANDIDATES", len(ranked))
            with col2:
                st.metric("AVERAGE SCORE", f"{avg:.1f}")
            with col3:
                st.metric("TOP SCORE", f"{ranked[0]['total_score']}")
            with col4:
                st.metric("TOP CANDIDATE", ranked[0]['name'])

            st.markdown('<div class="gold-divider"></div>',
                        unsafe_allow_html=True)

            # Table
            st.markdown("""
            <div style="font-size:0.7rem; letter-spacing:3px;
                 text-transform:uppercase; color:#666680;
                 margin-bottom:0.8rem;">
                Candidate Rankings
            </div>
            """, unsafe_allow_html=True)

            df = pd.DataFrame(ranked)
            display_df = df[[
                'name', 'email', 'total_score',
                'skills_score', 'experience_score',
                'education_score', 'education',
                'experience_years'
            ]].copy()
            display_df.columns = [
                'Name', 'Email', 'Total Score',
                'Skills', 'Experience',
                'Education Score', 'Qualification',
                'Years Exp'
            ]
            display_df.index = range(1, len(display_df) + 1)
            st.dataframe(display_df, use_container_width=True)

            st.markdown('<div class="gold-divider"></div>',
                        unsafe_allow_html=True)

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="font-size:0.7rem; letter-spacing:3px;
                     text-transform:uppercase; color:#666680;
                     margin-bottom:0.8rem;">
                    Score Comparison
                </div>
                """, unsafe_allow_html=True)
                fig = px.bar(
                    display_df,
                    x='Name',
                    y='Total Score',
                    color='Total Score',
                    color_continuous_scale=[
                        '#1a1a28', '#c9a96e', '#f0d080'
                    ]
                )
                fig.update_layout(
                    plot_bgcolor='#0d0d14',
                    paper_bgcolor='#0d0d14',
                    font_color='#a0a0b8',
                    font_family='Inter',
                    xaxis=dict(
                        gridcolor='#1e1e2e',
                        linecolor='#1e1e2e'
                    ),
                    yaxis=dict(
                        gridcolor='#1e1e2e',
                        linecolor='#1e1e2e'
                    ),
                    margin=dict(t=20, b=20, l=10, r=10)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("""
                <div style="font-size:0.7rem; letter-spacing:3px;
                     text-transform:uppercase; color:#666680;
                     margin-bottom:0.8rem;">
                    Top Candidate Breakdown
                </div>
                """, unsafe_allow_html=True)
                top = ranked[0]
                breakdown_df = pd.DataFrame({
                    'Category': [
                        'Skills', 'Experience', 'Education'
                    ],
                    'Score': [
                        top['skills_score'],
                        top['experience_score'],
                        top['education_score']
                    ]
                })
                fig = px.pie(
                    breakdown_df,
                    values='Score',
                    names='Category',
                    color_discrete_sequence=[
                        '#c9a96e', '#8b6914', '#f0d080'
                    ],
                    hole=0.6
                )
                fig.update_layout(
                    plot_bgcolor='#0d0d14',
                    paper_bgcolor='#0d0d14',
                    font_color='#a0a0b8',
                    font_family='Inter',
                    showlegend=True,
                    legend=dict(
                        font=dict(color='#a0a0b8')
                    ),
                    margin=dict(t=20, b=20, l=10, r=10)
                )
                fig.add_annotation(
                    text=f"<b>{top['total_score']}</b>",
                    x=0.5, y=0.5,
                    font=dict(
                        size=24,
                        color='#c9a96e',
                        family='Playfair Display'
                    ),
                    showarrow=False
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="gold-divider"></div>',
                        unsafe_allow_html=True)

            # Candidate cards
            st.markdown("""
            <div style="font-size:0.7rem; letter-spacing:3px;
                 text-transform:uppercase; color:#666680;
                 margin-bottom:1rem;">
                Candidate Profiles
            </div>
            """, unsafe_allow_html=True)

            for i, candidate in enumerate(ranked):
                rank_label = (
                    "01" if i == 0 else
                    "02" if i == 1 else
                    "03" if i == 2 else
                    f"0{i+1}" if i < 9 else str(i+1)
                )

                score = candidate['total_score']
                if score >= 70:
                    badge_class = "badge-gold"
                    badge_text = "Strong Match"
                elif score >= 40:
                    badge_class = "badge-silver"
                    badge_text = "Moderate Match"
                else:
                    badge_class = "badge-bronze"
                    badge_text = "Weak Match"

                with st.expander(
                    f"{rank_label}  ·  {candidate['name']}  ·  {score} pts"
                ):
                    st.markdown(
                        f'<span class="badge {badge_class}">{badge_text}</span>',
                        unsafe_allow_html=True
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("""
                        <div style="font-size:0.65rem;
                             letter-spacing:3px; color:#666680;
                             text-transform:uppercase;
                             margin-bottom:0.5rem;">
                             Contact
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="color:#a0a0b8; font-size:0.85rem; line-height:1.8">'
                            f'{candidate["email"]}<br>'
                            f'{candidate["phone"]}</div>',
                            unsafe_allow_html=True
                        )

                    with col2:
                        st.markdown("""
                        <div style="font-size:0.65rem;
                             letter-spacing:3px; color:#666680;
                             text-transform:uppercase;
                             margin-bottom:0.5rem;">
                             Background
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="color:#a0a0b8; font-size:0.85rem; line-height:1.8">'
                            f'{candidate["education"]}<br>'
                            f'{candidate["experience_years"]} years experience</div>',
                            unsafe_allow_html=True
                        )

                    with col3:
                        st.markdown("""
                        <div style="font-size:0.65rem;
                             letter-spacing:3px; color:#666680;
                             text-transform:uppercase;
                             margin-bottom:0.5rem;">
                             Score Breakdown
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="color:#a0a0b8; font-size:0.85rem; line-height:1.8">'
                            f'Skills &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {candidate["skills_score"]} / 60<br>'
                            f'Experience &nbsp; {candidate["experience_score"]} / 25<br>'
                            f'Education &nbsp;&nbsp; {candidate["education_score"]} / 15</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown("<br>", unsafe_allow_html=True)

                    if candidate['matched_skills']:
                        st.markdown("""
                        <div style="font-size:0.65rem;
                             letter-spacing:3px; color:#666680;
                             text-transform:uppercase;
                             margin-bottom:0.5rem;">
                             Matched Skills
                        </div>
                        """, unsafe_allow_html=True)
                        skills_html = "".join([
                            f'<span style="display:inline-block; margin:0.2rem 0.3rem; padding:0.2rem 0.8rem; border:1px solid #c9a96e; border-radius:2px; font-size:0.75rem; color:#c9a96e; letter-spacing:1px;">{s}</span>'
                            for s in candidate['matched_skills']
                        ])
                        st.markdown(
                            skills_html,
                            unsafe_allow_html=True
                        )

                    if candidate['resume_skills']:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("""
                        <div style="font-size:0.65rem;
                             letter-spacing:3px; color:#666680;
                             text-transform:uppercase;
                             margin-bottom:0.5rem;">
                             All Skills
                        </div>
                        """, unsafe_allow_html=True)
                        all_html = "".join([
                            f'<span style="display:inline-block; margin:0.2rem 0.3rem; padding:0.2rem 0.8rem; border:1px solid #2a2a3e; border-radius:2px; font-size:0.75rem; color:#666680; letter-spacing:1px;">{s}</span>'
                            for s in candidate['resume_skills']
                        ])
                        st.markdown(
                            all_html,
                            unsafe_allow_html=True
                        )

# ── PAGE 2 — PREVIOUS RESULTS ──
elif page == "Previous Results":

    st.markdown(
        '<div class="section-label">History</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-heading">Previous Screenings</div>',
        unsafe_allow_html=True
    )

    searches = get_all_searches()

    if not searches:
        st.info("No previous screenings found.")
    else:
        for search in searches:
            with st.expander(
                f"{search[1]}  ·  {search[2]}"
            ):
                results = get_search_results(search[0])
                if results:
                    results_data = [{
                        'Name': r[3],
                        'Email': r[4],
                        'Total Score': r[6],
                        'Qualification': r[13],
                        'Years Exp': r[12]
                    } for r in results]

                    df = pd.DataFrame(results_data)
                    df.index = range(1, len(df) + 1)
                    st.dataframe(df, use_container_width=True)

                    fig = px.bar(
                        df,
                        x='Name',
                        y='Total Score',
                        color='Total Score',
                        color_continuous_scale=[
                            '#1a1a28', '#c9a96e', '#f0d080'
                        ]
                    )
                    fig.update_layout(
                        plot_bgcolor='#0d0d14',
                        paper_bgcolor='#0d0d14',
                        font_color='#a0a0b8',
                        margin=dict(t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)