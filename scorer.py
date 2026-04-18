import re

SKILLS_DATABASE = [
    'Python', 'Java', 'JavaScript', 'C++', 'C#', 'R',
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite',
    'Data Analytics', 'Data Science', 'Data Engineering',
    'Machine Learning', 'Deep Learning', 'Artificial Intelligence',
    'Natural Language Processing', 'NLP', 'Computer Vision',
    'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Plotly',
    'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch',
    'Streamlit', 'Flask', 'Django', 'FastAPI',
    'Excel', 'Power BI', 'Tableau', 'Git', 'GitHub',
    'Docker', 'AWS', 'Azure', 'GCP', 'Jupyter',
    'HTML', 'CSS', 'React', 'Node.js', 'REST API',
    'Agile', 'Scrum', 'Linux'
]


def extract_skills_nlp(text):
    found_skills = []
    for skill in SKILLS_DATABASE:
        if skill.lower() in text.lower():
            found_skills.append(skill)
    return list(set(found_skills))


def extract_experience_years(text):
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
    text_lower = text.lower()
    if 'phd' in text_lower or 'doctorate' in text_lower:
        return 'PhD'
    elif 'mba' in text_lower:
        return 'MBA'
    elif 'master' in text_lower or 'm.tech' in text_lower:
        return 'Masters'
    elif ('bachelor' in text_lower or 'b.tech' in text_lower
          or 'bca' in text_lower or 'b.e' in text_lower):
        return 'Bachelors'
    elif 'diploma' in text_lower:
        return 'Diploma'
    else:
        return 'Not specified'


def score_resume(resume_data, job_description):
    score = 0
    breakdown = {}

    job_skills = extract_skills_nlp(job_description)
    resume_skills = extract_skills_nlp(resume_data['raw_text'])

    if job_skills:
        matched_skills = [
            s for s in resume_skills if s in job_skills
        ]
        skills_score = (len(matched_skills) / len(job_skills)) * 60
        score += skills_score
        breakdown['matched_skills'] = matched_skills
        breakdown['skills_score'] = round(skills_score, 2)
    else:
        breakdown['matched_skills'] = []
        breakdown['skills_score'] = 0

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

    education = extract_education(resume_data['raw_text'])
    edu_scores = {
        'PhD': 15, 'MBA': 14, 'Masters': 13,
        'Bachelors': 10, 'Diploma': 7, 'Not specified': 3
    }
    edu_score = edu_scores.get(education, 3)
    score += edu_score
    breakdown['education'] = education
    breakdown['education_score'] = edu_score
    breakdown['total_score'] = round(score, 2)
    breakdown['resume_skills'] = resume_skills

    return breakdown


def rank_resumes(resumes_data, job_description):
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
    ranked = sorted(
        ranked,
        key=lambda x: x['total_score'],
        reverse=True
    )
    return ranked