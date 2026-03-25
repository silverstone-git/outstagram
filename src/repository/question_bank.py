from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ...lib.models import Topic, Question, QuestionType
from ...lib.schemas import QuestionCreate, TopicPublic, QuestionPublic
from typing import List
import random
from uuid import uuid4

def get_topics_with_stats(db: Session) -> List[TopicPublic]:
    results = db.query(
        Topic.name, 
        Topic.slug, 
        func.count(Question.id).label("count")
    ).outerjoin(Question).group_by(Topic.topic_id).all()
    
    return [TopicPublic(name=r.name, slug=r.slug, count=r.count) for r in results]

def sample_questions_from_topic(db: Session, topic_slug: str, count: int) -> List[QuestionPublic]:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        return []
    
    # func.random() works for PostgreSQL
    questions = db.query(Question).filter(Question.topic_id == topic.topic_id).order_by(func.random()).limit(count).all()
    
    return [
        QuestionPublic(
            id=q.id,
            type=q.type,
            question=q.question,
            options=q.options,
            answer_label=q.answer_label,
            answer_labels=q.answer_labels,
            answer_range=q.answer_range,
            answer_value=q.answer_value,
            topic=topic.name,
            explanation=q.explanation,
            image_path=q.image_path
        ) for q in questions
    ]

def add_questions_to_topic(db: Session, topic_slug: str, questions: List[QuestionCreate]) -> dict:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        # Create topic if it doesn't exist, using slug as name if name not provided
        topic = Topic(name=topic_slug.replace("_", " ").title(), slug=topic_slug)
        db.add(topic)
        db.commit()
        db.refresh(topic)
    
    added_count = 0
    for q_data in questions:
        new_q = Question(
            id=str(uuid4()),
            type=q_data.type,
            question=q_data.question,
            options=q_data.options,
            answer_label=q_data.answer_label,
            answer_labels=q_data.answer_labels,
            answer_range=q_data.answer_range,
            answer_value=q_data.answer_value,
            topic_id=topic.topic_id,
            explanation=q_data.explanation,
            image_path=q_data.image_path
        )
        db.add(new_q)
        added_count += 1
    
    db.commit()
    
    total_count = db.query(func.count(Question.id)).filter(Question.topic_id == topic.topic_id).scalar()
    
    return {"success": True, "added": added_count, "total": total_count}
