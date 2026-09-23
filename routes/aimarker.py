from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,Query
)

from sqlalchemy.orm import Session

from app.dbconfig.database import get_db
from app.dbconfig.models import EssayMarking
from auth.security import require_admin


# import ai  
from app.ai.essay_marker import mark_essay_with_ai

ai_router = APIRouter(
    prefix="/admin",
    tags=["AI Essay Marking"]
)

@ai_router.post("/mark-essay")
async def mark_essay(
    student_name: str = Form(...),
    course: str = Form(...),
    exam_title: str = Form(...),
    question: str = Form(...),
    max_score: int = Form(...),
    answer_file: UploadFile = File(...),

    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    # ==================================
    # VALIDATE MAX SCORE
    # ==================================

    if max_score <= 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum score must be greater than zero."
        )

    # ==================================
    # VALIDATE FILE
    # ==================================

    if not answer_file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a student answer file."
        )

    filename = answer_file.filename.lower()

    allowed_extensions = (
        ".pdf",
        ".docx",
        ".txt"
    )

    if not filename.endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX and TXT files are supported."
        )

    # ==================================
    # READ FILE
    # ==================================

    file_content = await answer_file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # ==================================
    # EXTRACT TEXT
    # ==================================

    extracted_text = ""

    # TXT
    if filename.endswith(".txt"):

        extracted_text = file_content.decode(
            "utf-8",
            errors="ignore"
        )

    # PDF
    elif filename.endswith(".pdf"):

        import pymupdf

        try:

            pdf = pymupdf.open(
                stream=file_content,
                filetype="pdf"
            )

            pages = []

            for page in pdf:

                text = page.get_text()

                if text:
                    pages.append(text)

            extracted_text = "\n".join(pages)

            pdf.close()

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=f"Unable to read PDF: {str(e)}"
            )

    # DOCX
    elif filename.endswith(".docx"):

        from io import BytesIO
        from docx import Document

        try:

            document = Document(
                BytesIO(file_content)
            )

            paragraphs = []

            for paragraph in document.paragraphs:

                text = paragraph.text.strip()

                if text:
                    paragraphs.append(text)

            extracted_text = "\n".join(paragraphs)

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=f"Unable to read DOCX: {str(e)}"
            )

    # ==================================
    # CHECK EXTRACTED TEXT
    # ==================================

    extracted_text = extracted_text.strip()

    if not extracted_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract text from "
                "the student's answer file."
            )
        )

    # ==================================
    # AI MARKING

    try:
        ai_result = mark_essay_with_ai(
        question=question,
        student_answer=extracted_text,
        max_score=max_score
    )

    except Exception as e:
     raise HTTPException(
        status_code=500,
        detail=f"AI marking failed: {str(e)}"
    )
    score = ai_result["score"]
    percentage = ai_result["percentage"]

    grade = ai_result["grade"]

    feedback = ai_result["feedback"]

    strengths = ai_result["strengths"]

    improvements = ai_result["improvements"]
    # ==================================
    # SAVE REPORT TO DATABASE
    # ==================================

    report = EssayMarking(
    student_name=student_name,
    course=course,
    exam_title=exam_title,
    question=question,
    extracted_text=extracted_text,
    score=score,
    max_score=max_score,
    percentage=percentage,
    grade=grade,
    feedback=feedback,
    strengths="\n".join(strengths),
    improvements="\n".join(improvements),
    filename=answer_file.filename
        )
    try:

        db.add(report)
        db.commit()
        db.refresh(report)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save marking report: {str(e)}"
        )

    # ==================================
    # RETURN RESULT
    # ==================================

    return {
        "message": "Essay marked and report saved successfully",

        "report_id": report.id,

        "student_name": report.student_name,

        "course": report.course,

        "exam_title": report.exam_title,

        "question": report.question,

        "filename": report.filename,

        "score": report.score,

        "max_score": report.max_score,

        "percentage": report.percentage,

        "grade": report.grade,

        "feedback": report.feedback,

        "strengths": report.strengths,

        "improvements": report.improvements,

        "answer_length": len(report.extracted_text),

        "created_at": report.created_at,
    }

# report routes 

@ai_router.get("/reports")
def get_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    offset = (page - 1) * limit

    total = db.query(EssayMarking).count()

    reports = (
        db.query(EssayMarking)
        .order_by(EssayMarking.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "reports": [
            {
                "id": report.id,
                "student_name": report.student_name,
                "course": report.course,
                "exam_title": report.exam_title,
                "question": report.question,
                "score": float(report.score) if report.score is not None else 0,
                "max_score": float(report.max_score),
                "percentage": float(report.percentage)
                    if report.percentage is not None else 0,
                "grade": report.grade,
                "feedback": report.feedback,
                "strengths": report.strengths,
                "improvements": report.improvements,
                "filename": report.filename,
                "created_at": report.created_at
            }
            for report in reports
        ]
    }
# Important: because this is intended for university examination marking, 
# I would treat the AI output as AI-assisted marking, not an unquestionable
# final grade. You can build a lecturer/admin review step where the lecturer 
# can inspect the extracted answer, AI rationale, and score before finalizing 
# the result.