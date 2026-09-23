from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from app.dbconfig.database import get_db
from app.dbconfig.models import User, EssayMarking
from auth.security import require_admin


studentrouter = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@studentrouter.get("/admin")
def get_all_students(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.name.asc())
        .all()
    )

    students = []

    for user in users:

        results = (
            db.query(EssayMarking)
            .filter(
                EssayMarking.student_name == user.name
            )
            .order_by(
                EssayMarking.created_at.desc()
            )
            .all()
        )

        students.append({

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "role": user.role,

            "total_examinations": len(results),

            "results": [

                {
                    "id": report.id,

                    "course": report.course,

                    "exam_title": report.exam_title,

                    "score": (
                        float(report.score)
                        if report.score is not None
                        else 0
                    ),

                    "max_score": (
                        float(report.max_score)
                        if report.max_score is not None
                        else 0
                    ),

                    "percentage": (
                        float(report.percentage)
                        if report.percentage is not None
                        else 0
                    ),

                    "grade": report.grade,

                    "feedback": report.feedback,

                    "strengths": report.strengths,

                    "improvements": report.improvements,

                    "filename": report.filename,

                    "created_at": report.created_at
                }

                for report in results
            ]
        })

    return {
        "total_users": len(students),
        "students": students
    }
# Get student's examination results
@studentrouter.get("/results")
def get_student_results(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    reports = (
        db.query(EssayMarking)
        .filter(
            EssayMarking.student_name == current_user.name
        )
        .order_by(EssayMarking.created_at.desc())
        .all()
    )

    return {
        "total": len(reports),
        "results": [
            {
                "id": report.id,
                "course": report.course,
                "exam_title": report.exam_title,
                "score": float(report.score) if report.score else 0,
                "max_score": float(report.max_score),
                "percentage": float(report.percentage)
                if report.percentage else 0,
                "grade": report.grade,
                "feedback": report.feedback,
                "strengths": report.strengths,
                "improvements": report.improvements,
                "created_at": report.created_at
            }
            for report in reports
        ]
    }


# # Get one examination result
# @studentrouter.get("/results/{report_id}")
# def get_student_result(
#     report_id: int,
#     current_user: User = Depends(require_admin),
#     db: Session = Depends(get_db)
# ):
#     report = (
#         db.query(EssayMarking)
#         .filter(
#             EssayMarking.id == report_id,
#             EssayMarking.student_name == current_user.name
#         )
#         .first()
#     )

#     if not report:
#         from fastapi import HTTPException

#         raise HTTPException(
#             status_code=404,
#             detail="Result not found"
#         )

#     return {
#         "id": report.id,
#         "student_name": report.student_name,
#         "course": report.course,
#         "exam_title": report.exam_title,
#         "question": report.question,
#         "score": float(report.score) if report.score else 0,
#         "max_score": float(report.max_score),
#         "percentage": float(report.percentage)
#         if report.percentage else 0,
#         "grade": report.grade,
#         "feedback": report.feedback,
#         "strengths": report.strengths,
#         "improvements": report.improvements,
#         "filename": report.filename,
#         "created_at": report.created_at
#     }


# individual student single for editing 
@studentrouter.get("/results/{report_id}")
def get_result(
    report_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = (
        db.query(EssayMarking)
        .filter(EssayMarking.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )

    return {
        "id": report.id,
        "student_name": report.student_name,
        "course": report.course,
        "exam_title": report.exam_title,
        "score": float(report.score or 0),
        "max_score": float(report.max_score or 0),
        "percentage": float(report.percentage or 0),
        "grade": report.grade or "",
        "feedback": str(report.feedback or ""),
        "strengths": str(report.strengths or ""),
        "improvements": str(report.improvements or ""),
    }



# update route 
@studentrouter.put("/results/{report_id}")
def update_result(
    report_id: int,
    data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = (
        db.query(EssayMarking)
        .filter(EssayMarking.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )

    report.score = data.get("score")
    report.max_score = data.get("max_score")
    report.percentage = data.get("percentage")
    report.grade = data.get("grade")
    report.feedback = data.get("feedback")
    report.strengths = data.get("strengths")
    report.improvements = data.get("improvements")

    db.commit()
    db.refresh(report)

    return {
        "message": "Result updated successfully",
        "id": report.id
    }


# delete individual student 
@studentrouter.delete("/results/{report_id}")
def delete_result(
    report_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = (
        db.query(EssayMarking)
        .filter(EssayMarking.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )

    db.delete(report)
    db.commit()

    return {
        "success": True,
        "message": "Result deleted successfully",
        "id": report_id
    }