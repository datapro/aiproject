import json

from google import genai

from app.dbconfig.schemas import settings


client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)


def mark_essay_with_ai(
    question: str,
    student_answer: str,
    max_score: int
):

    prompt = f"""
You are an AI-assisted university examination marking system.

Evaluate the student's answer against the examination question.

IMPORTANT:
- Mark only the submitted answer.
- Do not invent information.
- Consider correctness, relevance, depth,
  organization, clarity, evidence and understanding.
- Give a fair academic assessment.
- Maximum available score: {max_score}
- Score must be between 0 and {max_score}.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not wrap the JSON in ```json.

EXAMINATION QUESTION:
{question}

STUDENT ANSWER:
{student_answer}

Return exactly:

{{
    "score": 0,
    "feedback": "Overall assessment of the answer.",
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2"
    ]
}}

Grading scale:

70-100 = A
60-69 = B
50-59 = C
45-49 = D
40-44 = E
0-39 = F
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    content = interaction.output_text

    if not content:
        raise ValueError(
            "Gemini returned an empty response."
        )

    content = content.strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON: {content}"
        ) from e

    try:
        score = float(result["score"])

    except (KeyError, TypeError, ValueError) as e:
        raise ValueError(
            "Gemini returned an invalid score."
        ) from e

    # Keep score within allowed range
    score = max(
        0,
        min(score, max_score)
    )

    percentage = round(
        (score / max_score) * 100,
        2
    )

    if percentage >= 70:
        grade = "A"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 50:
        grade = "C"
    elif percentage >= 45:
        grade = "D"
    elif percentage >= 40:
        grade = "E"
    else:
        grade = "F"

    return {
        "score": score,
        "percentage": percentage,
        "grade": grade,
        "feedback": result.get(
            "feedback",
            ""
        ),
        "strengths": result.get(
            "strengths",
            []
        ),
        "improvements": result.get(
            "improvements",
            []
        )
    }