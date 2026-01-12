import PyPDF2
from docx import Document
import re


def clean_text(text):
    # Supprimer les caractères spéciaux
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def extract_text_from_pdf(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du PDF: {str(e)}")


def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du DOCX: {str(e)}")


def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Format de fichier non supporté. Utilisez PDF ou DOCX.")


def extract_skills(text):
    # Liste de compétences courantes
    skills_keywords = [
        # Langages de programmation
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Swift',
        # Frameworks
        'Django', 'Flask', 'React', 'Angular', 'Vue', 'Spring', 'Laravel',
        # Bases de données
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis',
        # Outils
        'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'Jenkins',
        # Data Science
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
        # Autres
        'Excel', 'PowerBI', 'Tableau', 'SEO', 'Marketing', 'Agile', 'Scrum'
    ]

    found_skills = []
    text_lower = text.lower()

    for skill in skills_keywords:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return list(set(found_skills))