import spacy
import re
from extractor import extract_skills

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Master skills database
SKILLS_DATABASE = [
    # Programming Languages
    'Python', 'Java', 'JavaScript', 'C++', 'C#', 'R', 'Swift',
    'Kotlin', 'PHP', 'Ruby', 'Scala', 'Go',

    # Data Skills
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite',
    'Data Analytics', 'Data Science', 'Data Engineering',
    'Machine Learning', 'Deep Learning', 'Artificial Intelligence',
    'Natural Language Processing', 'NLP', 'Computer Vision',

    # Python Libraries
    'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Plotly',
    'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch',
    'Streamlit', 'Flask', 'Django', 'FastAPI',

    # Tools
    'Excel', 'Power BI', 'Tableau', 'Git', 'GitHub',
    'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
    'Jupyter', 'VS Code', 'PyCharm',

    # Other Skills
    'HTML', 'CSS', 'React', 'Angular', 'Node.js',
    'REST API', 'Agile', 'Scrum', 'Linux', 'Windows'
]


def extract_skills_nlp(text):
    """
    Extract skills using spaCy NLP
    """
    # Process text with spaCy
    doc = nlp(text.lower())

    found_skills = []

    # Match skills from database
    for skill in SKILLS_DATABASE:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    # Remove duplicates
    found_skills = list(set(found_skills))

    return found_skills


def extract_experience_years(text):
    """
    Extract years of experience from resume
    """
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'experience\s*of\s*(\d+)\+?\s*years?',
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))

    return 0


def extract_education(text):
    """
    Extract education level from resume
    """
    text_lower = text.lower()

    if 'phd' in text_lower or 'doctorate' in text_lower:
        return 'PhD'
    elif 'mba' in text_lower:
        return 'MBA'
    elif 'master' in text_lower or 'm.tech' in text_lower:
        return 'Masters'
    elif 'bachelor' in text_lower or 'b.tech' in text_lower or 'bca' in text_lower or 'b.e' in text_lower:
        return 'Bachelors'
    elif 'diploma' in text_lower:
        return 'Diploma'
    else:
        return 'Not specified'


def score_resume(resume_data, job_description):
    """
    Score a resume against job description
    Returns score out of 100
    """
    score = 0
    breakdown = {}

    # Extract skills from job description
    job_skills = extract_skills_nlp(job_description)

    # Extract skills from resume
    resume_skills = extract_skills_nlp(resume_data['raw_text'])

    # 1. Skills match score (60 points)
    if job_skills:
        matched_skills = [
            skill for skill in resume_skills
            if skill in job_skills
        ]
        skills_score = (len(matched_skills) / len(job_skills)) * 60
        score += skills_score
        breakdown['matched_skills'] = matched_skills
        breakdown['skills_score'] = round(skills_score, 2)
    else:
        breakdown['matched_skills'] = []
        breakdown['skills_score'] = 0

    # 2. Experience score (25 points)
    exp_years = extract_experience_years(resume_data['raw_text'])
    if exp_years >= 5:
        exp_score = 25
    elif exp_years >= 3:
        exp_score = 20
    elif exp_years >= 1:
        exp_score = 15
    else:
        exp_score = 5
    score += exp_score
    breakdown['experience_years'] = exp_years
    breakdown['experience_score'] = exp_score

    # 3. Education score (15 points)
    education = extract_education(resume_data['raw_text'])
    education_scores = {
        'PhD': 15,
        'MBA': 14,
        'Masters': 13,
        'Bachelors': 10,
        'Diploma': 7,
        'Not specified': 3
    }
    edu_score = education_scores.get(education, 3)
    score += edu_score
    breakdown['education'] = education
    breakdown['education_score'] = edu_score

    # Final score
    breakdown['total_score'] = round(score, 2)
    breakdown['resume_skills'] = resume_skills

    return breakdown


def rank_resumes(resumes_data, job_description):
    """
    Score and rank all resumes
    """
    ranked = []

    for resume in resumes_data:
        score_data = score_resume(resume, job_description)
        ranked.append({
            'file_name': resume['file_name'],
            'name': resume['name'],
            'email': resume['email'],
            'phone': resume['phone'],
            'total_score': score_data['total_score'],
            'skills_score': score_data['skills_score'],
            'experience_score': score_data['experience_score'],
            'education_score': score_data['education_score'],
            'matched_skills': score_data['matched_skills'],
            'resume_skills': score_data['resume_skills'],
            'experience_years': score_data['experience_years'],
            'education': score_data['education']
        })

    # Sort by total score highest first
    ranked = sorted(ranked,
                   key=lambda x: x['total_score'],
                   reverse=True)

    return ranked