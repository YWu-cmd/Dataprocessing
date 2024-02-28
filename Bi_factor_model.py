from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pandas as pd
from collections import defaultdict
import numpy as np
import openpyxl

# Assuming necessary ORM declarations are defined in Database.py
from Database import Answer, question_survey_relation

class SymptomSurveyDataProcessor:
    def __init__(self, database_url):
        self.database_url = database_url
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def fetch_earliest_answers_for_survey(self, survey_id, symptom_to_questions):
        user_ids = [uid[0] for uid in self.session.query(Answer.user_id).distinct().all()]

        data_for_df = []

        for user_id in user_ids:
            user_data = {'user_id': user_id}
            for symptom_id, qsr_ids in symptom_to_questions.items():
                for qsr_id in qsr_ids:
                    # Fetch the earliest answer for this QSR ID for the current user
                    earliest_answer = self.session.query(
                        Answer.option_id
                    ).filter(
                        Answer.user_id == user_id,
                        Answer.qsr_id == qsr_id,
                        question_survey_relation.c.survey_id == survey_id
                    ).join(
                        question_survey_relation, question_survey_relation.c.qsr_id == Answer.qsr_id
                    ).order_by(
                        Answer.create_date
                    ).first()

                    if earliest_answer:
                        column_name = f'S{symptom_id}_{qsr_id}'
                        user_data[column_name] = earliest_answer[0]

            data_for_df.append(user_data)

        df = pd.DataFrame(data_for_df).fillna(0)
        return df

if __name__ == "__main__":
    database_url = "sqlite:///survey_system.db"
    survey_id = 1
    symptom_to_questions = {
        1: [6, 11, 13, 24, 39],
        2: [3, 9, 11, 12, 18, 20, 15, 32, 40],
        3: [2, 5, 11, 22, 25, 28, 30],
        4: [10, 33, 36],
        5: [4, 8, 16],
        6: [21, 23, 27, 35, 42, 43, 44],
        7: [1, 7, 14, 26],
        8: [17, 19, 31, 34, 37],
    }

    with SymptomSurveyDataProcessor(database_url) as processor:
        df = processor.fetch_earliest_answers_for_survey(survey_id, symptom_to_questions)
        # Save the DataFrame to a CSV file
        df.to_csv('survey_earliest_answers.csv', index=False)
        print("Data saved to 'survey_earliest_answers.csv'")

