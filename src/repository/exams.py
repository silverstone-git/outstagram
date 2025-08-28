from sqlalchemy.orm import Session
from ...lib.models import Exam

def get_all_exams_paginated(db: Session, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    return db.query(
        Exam.exam_id, 
        Exam.exam_title, 
        Exam.datetime_uploaded
    ).order_by(Exam.datetime_uploaded.desc()).offset(offset).limit(page_size).all()
