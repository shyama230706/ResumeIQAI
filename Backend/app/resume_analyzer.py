import re

SECTION_KEYWORDS = {
    "Contact Information": [],
    "Professional Summary": [
        "summary",
        "objective",
        "profile"
    ],
    "Skills": [
        "skills",
        "technical skills"
    ],
    "Education": [
        "education",
        "academic",
        "qualification"
    ],
    "Experience": [
        "experience",
        "work experience",
        "employment",
        "internship"
    ],
    "Projects": [
        "projects",
        "project"
    ],
    "Certifications": [
        "certification",
        "certifications",
        "certificate"
    ],
    "Achievements": [
        "achievement",
        "achievements",
        "award",
        "awards"
    ]
}


def analyze_resume(resume_text):

    text = resume_text.lower()

    found_sections = []
    missing_sections = []

    # ---------- Contact ----------

    email = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone = re.search(
        r"\+?\d[\d\s\-]{8,}",
        text
    )

    if email or phone:
        found_sections.append("Contact Information")
    else:
        missing_sections.append("Contact Information")

    # ---------- Other Sections ----------

    for section, keywords in SECTION_KEYWORDS.items():

        if section == "Contact Information":
            continue

        found = False

        for keyword in keywords:

            if keyword in text:
                found = True
                break

        if found:
            found_sections.append(section)
        else:
            missing_sections.append(section)

    score = round(
        (len(found_sections) / len(SECTION_KEYWORDS)) * 100,
        2
    )

    suggestions = []

    for section in missing_sections:
        suggestions.append(
            f"Add a '{section}' section to improve ATS."
        )

    return {
        "Section Score": score,
        "Found Sections": found_sections,
        "Missing Sections": missing_sections,
        "Section Suggestions": suggestions
    }