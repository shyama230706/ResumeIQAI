from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.skill_matcher import compare_skills


def calculate_ats_score(resume_text: str, job_description: str):
    """
    Calculate ATS score using TF-IDF + Cosine Similarity
    and compare resume skills with job description skills.
    """

    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

    ats_score = round(similarity * 100, 2)

    skill_data = compare_skills(resume_text, job_description)

    suggestions = []

    if len(skill_data["missing_skills"]) > 0:
        for skill in skill_data["missing_skills"]:
            suggestions.append(
                f"Consider adding '{skill}' if you have experience with it."
            )
    else:
        suggestions.append(
            "Excellent! Your resume matches the required skills."
        )

    return {
        "ATS Score": ats_score,
        "Resume Skills": skill_data["resume_skills"],
        "Matched Skills": skill_data["matched_skills"],
        "Missing Skills": skill_data["missing_skills"],
        "Suggestions": suggestions
    }