# skill_matcher.py

SKILLS_DATABASE = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "fastapi",
    "flask",
    "django",
    "react",
    "javascript",
    "html",
    "css",
    "node.js",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",
    "computer vision",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "power bi",
    "excel",
    "data analysis",
    "data visualization"
]


def extract_skills(text: str):
    """
    Extract skills from resume or job description.
    """

    text = text.lower()

    found_skills = []

    for skill in SKILLS_DATABASE:
        if skill in text:
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def compare_skills(resume_text: str, jd_text: str):
    """
    Compare resume skills with job description skills.
    """

    resume_skills = extract_skills(resume_text)

    jd_skills = extract_skills(jd_text)

    matched = []

    missing = []

    for skill in jd_skills:
        if skill in resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "resume_skills": resume_skills,
        "matched_skills": matched,
        "missing_skills": missing
    }