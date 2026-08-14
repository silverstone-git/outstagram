from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ...lib.models import Topic, Question, QuestionType, SectionQuestionLink, TopicGroup
from ...lib.schemas import QuestionCreate, TopicPublic, QuestionPublic
from typing import List, Dict
import random
from uuid import uuid4

def get_all_groups(db: Session) -> List[str]:
    groups = db.query(TopicGroup).all()
    return [group.name for group in groups]

def get_grouped_topics(db: Session, group_name: str = None) -> Dict[str, List[str]]:
    query = db.query(TopicGroup)
    if group_name:
        query = query.filter(TopicGroup.name == group_name)
    groups = query.all()
    
    result = {}
    for group in groups:
        result[group.name] = [topic.name for topic in group.topics]
    return result

def assign_topic_to_group(db: Session, topic_slug: str, group_name: str):
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    group = db.query(TopicGroup).filter(TopicGroup.name == group_name).first()
    if not group:
        group = TopicGroup(name=group_name)
        db.add(group)
        db.commit()
        db.refresh(group)
    if topic and group not in topic.groups:
        topic.groups.append(group)
        db.commit()

def get_topics_with_stats(db: Session) -> List[TopicPublic]:
    results = db.query(
        Topic.name, 
        Topic.slug, 
        func.count(Question.id).label("count")
    ).outerjoin(Question).group_by(Topic.topic_id).all()
    
    return [TopicPublic(name=r.name, slug=r.slug, count=r.count) for r in results]

def sample_questions_from_topic(db: Session, topic_slug: str, count: int, easy_count: int = 0, medium_count: int = 0, hard_count: int = 0) -> List[QuestionPublic]:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        return []

    sampled_questions = []

    # If specific counts are provided, use them for weighted sampling
    if easy_count > 0 or medium_count > 0 or hard_count > 0:
        if easy_count > 0:
            questions = db.query(Question).filter(Question.topic_id == topic.topic_id, Question.difficulty == 'easy').order_by(func.random()).limit(easy_count).all()
            sampled_questions.extend(questions)
        if medium_count > 0:
            questions = db.query(Question).filter(Question.topic_id == topic.topic_id, Question.difficulty == 'medium').order_by(func.random()).limit(medium_count).all()
            sampled_questions.extend(questions)
        if hard_count > 0:
            questions = db.query(Question).filter(Question.topic_id == topic.topic_id, Question.difficulty == 'hard').order_by(func.random()).limit(hard_count).all()
            sampled_questions.extend(questions)
    else:
        # Fallback to random sampling if no specific counts are provided
        sampled_questions = db.query(Question).filter(Question.topic_id == topic.topic_id).order_by(func.random()).limit(count).all()
    
    return [
        QuestionPublic(
            id=q.id,
            type=q.type,
            difficulty=q.difficulty,
            question=q.question,
            options=q.options,
            answer_label=q.answer_label,
            answer_labels=q.answer_labels,
            answer_range=q.answer_range,
            answer_value=q.answer_value,
            topic=topic.name,
            explanation=q.explanation,
            image_path=q.image_path
        ) for q in sampled_questions
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
            difficulty=q_data.difficulty,
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

def add_unique_questions_to_topic(db: Session, topic_slug: str, questions: List[QuestionCreate]) -> dict:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        topic = Topic(name=topic_slug.replace("_", " ").title(), slug=topic_slug)
        db.add(topic)
        db.commit()
        db.refresh(topic)
    
    # Get existing question texts for this topic to check for duplicates
    existing_questions = db.query(Question.question).filter(Question.topic_id == topic.topic_id).all()
    existing_question_texts = {q[0] for q in existing_questions}
    
    added_count = 0
    for q_data in questions:
        # Check if the question text already exists in this topic
        if q_data.question in existing_question_texts:
            continue
            
        new_q = Question(
            id=str(uuid4()),
            type=q_data.type,
            difficulty=q_data.difficulty,
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
        existing_question_texts.add(q_data.question) # Update set to avoid duplicates in the same batch
        added_count += 1
    
    db.commit()
    
    total_count = db.query(func.count(Question.id)).filter(Question.topic_id == topic.topic_id).scalar()
    
    return {"success": True, "added": added_count, "total": total_count}

def delete_questions_from_topic(db: Session, topic_slug: str) -> dict:
    topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
    if not topic:
        return {"success": False, "detail": "Topic not found"}
    
    # Find all question IDs for this topic
    questions = db.query(Question).filter(Question.topic_id == topic.topic_id).all()
    question_ids = [q.id for q in questions]
    
    if not question_ids:
        return {"success": True, "deleted": 0}
        
    # Delete links to exam sections
    db.query(SectionQuestionLink).filter(SectionQuestionLink.question_id.in_(question_ids)).delete(synchronize_session=False)
    
    # Delete the questions
    deleted_count = db.query(Question).filter(Question.topic_id == topic.topic_id).delete(synchronize_session=False)
    
    db.commit()
    
    return {"success": True, "deleted": deleted_count}
