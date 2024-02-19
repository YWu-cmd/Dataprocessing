from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your actual classes here
from Database import Question, Option

DATABASE_URL = "sqlite:///survey_system.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Options data
option_names = [
    "完全不像我", "不太像我", "有一些像我", "比较像我", "非常像我"
]

def create_options_for_questions():
    session = Session()
    try:
        # Fetch all question IDs
        question_ids = session.query(Question.question_id).all()

        for question_id in question_ids:
            # Iterate over the range of option IDs
            for option_id in range(5):
                option = Option(
                    question_id=question_id[0],
                    option_id=option_id,
                    option_name=option_names[option_id]
                )
                session.add(option)

        session.commit()
        print("Options created for all questions.")

    except Exception as e:
        session.rollback()
        print("An error occurred, rolling back the transaction:", e)
    finally:
        session.close()

if __name__ == "__main__":
    create_options_for_questions()
