from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from Database import Answer, Question, Symptom, Score, symptom_question_relation  # Import your SQLAlchemy models
from sqlalchemy.sql import exists

# Setup database connection
engine = create_engine('sqlite:///survey_system.db')
Session = sessionmaker(bind=engine)
session = Session()

# Fetch user attempts
user_attempts = session.query(Answer.user_id, Answer.create_date).distinct().order_by(Answer.user_id, Answer.create_date).all()

for user_id, attempt_date in user_attempts:
    # Fetch answers for this attempt
    answers = session.query(Answer).filter(Answer.user_id == user_id, func.date(Answer.create_date) == attempt_date.date()).all()
    
    symptom_scores = {}
    for answer in answers:
        # Find related question and symptom
        question_id = session.query(Question.question_id).join(Answer, Answer.qsr_id == Question.question_id).filter(Answer.answer_id == answer.answer_id).scalar()
        symptoms = session.query(Symptom).join(symptom_question_relation, Symptom.symptom_id == symptom_question_relation.c.symptom_id).filter(symptom_question_relation.c.question_id == question_id).all()
        
        # Calculate score, special handling for questions 22, 30, 14, 44
        score = answer.option_id if question_id not in [22, 30, 14, 44] else 4 - answer.option_id
        
        # Accumulate score for each related symptom
        for symptom in symptoms:
            if symptom.symptom_id not in symptom_scores:
                symptom_scores[symptom.symptom_id] = 0
            symptom_scores[symptom.symptom_id] += score

    # Record the scores for each symptom
    for symptom_id, total_score in symptom_scores.items():
        # Check if a score record already exists for this attempt
        score_record = session.query(Score).filter(Score.user_id == user_id, Score.symptom_id == symptom_id, Score.attempt_id == attempt_date).first()
        if score_record:
            score_record.score = total_score
        else:
            new_score = Score(user_id=user_id, attempt_id=attempt_date, symptom_id=symptom_id, score=total_score)
            session.add(new_score)
    
    session.commit()
