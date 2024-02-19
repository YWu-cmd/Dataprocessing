import random
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Import your actual classes here
from Database import User, Question, Option, Survey, Answer, question_survey_relation

DATABASE_URL = "sqlite:///survey_system.db"  # Your database connection string
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Constants for generating student answers
NUM_STUDENTS = 10000
NUM_QUESTIONS = 44
MEAN_SCORE = 2
STD_DEV_SCORE = 2/3
SURVEY_ID = 1  # Assuming a single survey for simplicity

def generate_random_birthday():
    # Generates a random birthday within a specified range
    start_date = datetime(1995, 1, 1)
    end_date = datetime(2005, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_student_answers():
    session = Session()
    try:
        question_ids = session.query(Question.question_id).join(question_survey_relation).filter(question_survey_relation.c.survey_id == SURVEY_ID).all()
        
        for student_id in range(1, NUM_STUDENTS + 1):
            birthday = generate_random_birthday()
            # Create a new user with a random birthday for each student
            user = User(name=f"Student_{student_id}", wechatID=f"wx{student_id}", birthday=birthday)
            session.add(user)
            session.flush()  # Ensures user_id is generated

            for question_id, in question_ids:
                # Generate a score based on a normal distribution and round it
                score = round(np.random.normal(MEAN_SCORE, STD_DEV_SCORE))
                # Ensure the score is within the valid range of 0-4
                score = max(min(score, 4), 0)
                
                # Create an answer record linking the score with option_id
                answer = Answer(
                    qsr_id=question_id,
                    user_id=user.user_id,
                    option_id=score,  # Directly use the score as option_id
                    test_duration=random.randint(5, 10),
                    create_date=datetime.utcnow()
                )
                session.add(answer)

            if student_id % 100 == 0:
                session.commit()  # Commit in batches to optimize performance
                print(f"Committed answers for {student_id} students.")

        session.commit()  # Final commit for any remaining records
    except Exception as e:
        session.rollback()  # Rollback in case of an error
        print("An error occurred, rolling back the transaction:", e)
    finally:
        session.close()  # Ensure the session is closed properly

if __name__ == "__main__":
    generate_student_answers()
