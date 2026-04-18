import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file
    """
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
           
            total_pages = len(pdf_reader.pages)
            print(f"Total pages in PDF: {total_pages}")
            
            # Extract text from each page
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
                
        return text
    
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def extract_name(text):
    """
    Extract candidate name from resume
    (assumes name is in first line)
    """
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 2 and len(line) < 50:
            return line
    return "Unknown"


def extract_email(text):
    """
    Extract email address from resume text
    """
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        return emails[0]
    return "Not found"


def extract_phone(text):
    """
    Extract phone number from resume text
    """
    import re
    phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    phones = re.findall(phone_pattern, text)
    if phones:
        return phones[0]
    return "Not found"


def extract_skills(text, skills_list):
    """
    Extract skills from resume text
    by matching against a skills list
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills


def process_resume(pdf_path, skills_list):
    """
    Process a single resume and return
    all extracted information
    """
    print(f"\nProcessing: {pdf_path}")
    
    # Extract raw text
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        return None
    
    # Extract all information
    resume_data = {
        'file_name': os.path.basename(pdf_path),
        'raw_text': text,
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text, skills_list)
    }
    
    return resume_data