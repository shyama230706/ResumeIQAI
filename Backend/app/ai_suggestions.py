def generate_feedback(matched, missing, ats_score):

    feedback = []

    if ats_score >= 80:
        feedback.append("Excellent resume. It is highly ATS friendly.")
    elif ats_score >= 60:
        feedback.append("Good resume, but it can be improved.")
    else:
        feedback.append("Your resume needs improvement to match this job.")

    if len(missing) > 0:
        feedback.append(
            "Try adding these important skills if you know them: "
            + ", ".join(missing)
        )

    if len(matched) > 0:
        feedback.append(
            "Strong skills found: "
            + ", ".join(matched)
        )

    feedback.append("Use action verbs in project descriptions.")

    feedback.append("Add measurable achievements whenever possible.")

    feedback.append("Keep the resume to one page.")

    return feedback