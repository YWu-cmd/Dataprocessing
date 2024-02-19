import random
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Import your actual classes here
from Database import User, Question, Option, Survey, Answer, question_survey_relation

DATABASE_URL = "sqlite:///survey_system.db"  # Replace with your actual database connection string
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Constants
NUM_ANSWER_SETS = 20
NUM_QUESTIONS = 44
MEAN_SCORE = 2
STD_DEV_SCORE = 2/3
SURVEY_ID = 1  # Assuming there's only one survey

def generate_answers_for_user(user_id):
    session = Session()
    try:
        # Fetch all question IDs from the survey
        question_ids = session.query(Question.question_id).join(question_survey_relation).filter(question_survey_relation.c.survey_id == SURVEY_ID).all()
        question_ids = [qid for (qid,) in question_ids]
        
        # Fetch the user, assuming it exists (no random birthday generation)
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            print(f"No user found with user_id {user_id}. Please ensure the user exists before generating answers.")
            return
        
        for set_num in range(NUM_ANSWER_SETS):
            # Generate a timestamp for the current set of answers
            current_set_timestamp = datetime.utcnow() + timedelta(days=set_num)

            # Generate answers with the same timestamp for each question in the set
            for question_id in question_ids:
                score = np.random.normal(MEAN_SCORE, STD_DEV_SCORE)
                score = max(min(round(score), 4), 0)  # Ensure score is within 0-4 range

                answer = Answer(
                    qsr_id=question_id,
                    user_id=user.user_id,
                    option_id=score,  # Here, option_id represents the score
                    create_date=current_set_timestamp,  # Same timestamp for all answers in the set
                    test_duration=random.randint(5, 10)  # Random duration between 5 and 10
                )
                session.add(answer)

            session.commit()  # Commit after each set
            print(f"Committed answer set {set_num + 1} for user {user_id}.")

    except Exception as e:
        session.rollback()
        print("An error occurred, rolling back the transaction:", e)
    finally:
        session.close()

if __name__ == "__main__":
    USER_ID = 1  # Replace with the user_id for which you want to generate the answer sets
    generate_answers_for_user(USER_ID)
