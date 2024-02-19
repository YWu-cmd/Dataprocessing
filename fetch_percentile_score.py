from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import numpy as np

class SurveyAnalysis:
    def __init__(self, db_url='sqlite:///survey_system.db'):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def calculate_scores_and_percentiles(self, user_id):
        session = self.Session()
        from Database import User, Score, Symptom  # Ensure Database.py contains the necessary model definitions

        user = session.query(User).filter(User.user_id == user_id).one()
        attempts_dates = session.query(Score.attempt_id).filter(Score.user_id == user_id).distinct().all()

        attempt_results = []
        for attempt_date in attempts_dates:
            # Parse the attempt_date string to datetime and format to 'YYYY-MM-DD'
            formatted_attempt_date = datetime.strptime(attempt_date[0], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d')
            
            attempt_data = {
                'name': user.name,
                'birthday': user.birthday.strftime('%Y-%m-%d'),
                'attempt_date': formatted_attempt_date,
                'symptom_scores': {}
            }

            for symptom in session.query(Symptom).all():
                user_score = session.query(Score.score).filter(
                    Score.user_id == user_id,
                    Score.symptom_id == symptom.symptom_id,
                    Score.attempt_id == attempt_date[0]
                ).scalar()

                if symptom.symptom_id <= 8:
                    num_users_with_lower_or_equal_scores = session.query(func.count(Score.user_id.distinct())).filter(
                        Score.symptom_id == symptom.symptom_id,
                        Score.score <= user_score
                    ).scalar()
                    total_users = session.query(func.count(Score.user_id.distinct())).filter(
                        Score.symptom_id == symptom.symptom_id
                    ).scalar()
                    
                    # Calculate the percentile, multiply by 100, and round to two decimal places
                    percentile = round((num_users_with_lower_or_equal_scores / total_users * 100), 2) if total_users else 0
                    attempt_data['symptom_scores'][symptom.symptom_id] = {'score': user_score, 'percentile': percentile}
                else:
                    attempt_data['symptom_scores'][symptom.symptom_id] = {'score': user_score}

            attempt_results.append(attempt_data)
        session.close()
        return attempt_results

    @staticmethod
    def print_results(results):
        for result in results:
            print(result)

def main(user_id):
    analysis = SurveyAnalysis()
    results = analysis.calculate_scores_and_percentiles(user_id)
    analysis.print_results(results)

if __name__ == '__main__':
    user_id = 1  # Replace with dynamic input as needed
    main(user_id)
