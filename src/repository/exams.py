from sqlalchemy.orm import Session
from ...lib.models import Exam, ExamSection, SectionQuestionLink, Question
from ...lib.schemas import ExamCreate, ExamPublic, ExamSectionPublic, QuestionPublic, Marking
from uuid import uuid4
from typing import List


def get_all_exams_paginated(db: Session, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    return db.query(
        Exam.exam_id,
        Exam.exam_title,
        Exam.datetime_uploaded
    ).order_by(Exam.datetime_uploaded.desc()).offset(offset).limit(page_size).all()


def create_exam_repo(db: Session, exam_data: ExamCreate) -> Exam:
    exam_id = str(uuid4())
    new_exam = Exam(
        exam_id=exam_id, 
        exam_title=exam_data.exam_title, 
        exam_json_str=exam_data.exam_json_str
    )
    db.add(new_exam)

    if exam_data.sections:
        for s_data in exam_data.sections:
            section_id = str(uuid4())
            new_section = ExamSection(
                id=section_id,
                name=s_data.name,
                exam_id=exam_id,
                marking_positive=s_data.marking.positive,
                marking_negative=s_data.marking.negative,
                max_attempts=s_data.max_attempts
            )
            db.add(new_section)
            for q_id in s_data.questions:
                link = SectionQuestionLink(section_id=section_id, question_id=q_id)
                db.add(link)

    db.commit()
    db.refresh(new_exam)
    return new_exam


def get_exam_full_repo(db: Session, exam_id: str) -> ExamPublic | None:
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        return None

    sections_public = []
    for section in exam.sections:
        questions_public = []
        for q in section.questions:
            questions_public.append(
                QuestionPublic(
                    id=q.id,
                    type=q.type,
                    question=q.question,
                    options=q.options,
                    answer_label=q.answer_label,
                    answer_labels=q.answer_labels,
                    answer_range=q.answer_range,
                    answer_value=q.answer_value,
                    topic=q.topic.name if q.topic else "Unknown",
                    explanation=q.explanation,
                    image_path=q.image_path
                )
            )
        sections_public.append(
            ExamSectionPublic(
                id=section.id,
                name=section.name,
                marking=Marking(positive=section.marking_positive, negative=section.marking_negative),
                max_attempts=section.max_attempts,
                questions=questions_public
            )
        )

    return ExamPublic(
        exam_id=exam.exam_id,
        exam_title=exam.exam_title,
        exam_json_str=exam.exam_json_str,
        sections=sections_public
    )

