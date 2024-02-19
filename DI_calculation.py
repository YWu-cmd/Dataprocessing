from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
# Assuming your SQLAlchemy models are defined in Database.py
from Database import Symptom, Question, Option, Answer, symptom_question_relation, question_survey_relation
from semopy import Model
import pandas as pd
import numpy as np
from SymptomSurveyOptionFetcher import SymptomSurveyOptionFetcher

class UserSymptomModeler:
    def __init__(self, user_id):
        self.user_id = user_id
        self.engine = create_engine('sqlite:///survey_system.db')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.survey_id = 1  # Assuming survey_id=1 is of interest

    def fetch_data(self, symptom_id):
        # Placeholder for actual data fetching logic
        fetcher = SymptomSurveyOptionFetcher(self.session)
        return fetcher.fetch_latest_options_for_symptom_and_survey(self.user_id, symptom_id, self.survey_id)

    def fit_models(self):
        results = {}
        # Assuming 8 symptoms for simplicity
        for symptom_id in range(1, 9):
            symptom_data = self.fetch_data(symptom_id)
            for date, option_ids in symptom_data.items():
                # Convert option_ids to DataFrame
                data = {f'Q{symptom_id}_{index}': [option] for index, option in enumerate(option_ids, start=1)}
                df = pd.DataFrame(data)
                df = df.add_prefix(f"S{symptom_id}_")
                
                # Construct model description
                specific_factors = " + ".join(df.columns)
                model_desc = f"S{symptom_id} =~ {specific_factors}\n"

                # Print the data and model description for inspection
                print(f"Data for Symptom S{symptom_id} on Date {date}:")
                print(df)
                print("Model Description:")
                print(model_desc)

                # Fit the model
                model = Model(model_desc)
                try:
                    model.load_dataset(df)
                    model.fit()
                    estimates = model.inspect()
                    print("Model Estimates:\n", estimates[['lval', 'rval', 'Estimate']])
                    results[date][f'Symptom_{symptom_id}'] = estimates
                except Exception as e:
                    print(f"Error fitting model for Symptom S{symptom_id} on Date {date}: {e}")
                    results[date][f'Symptom_{symptom_id}'] = 'Error during model fitting.'

        return results


    def construct_model_description(self, symptom_questions_map):
        model_desc = ""
        for symptom_id, num_questions in symptom_questions_map.items():
            questions_desc = " + ".join([f'Q{symptom_id}_{i}' for i in range(1, num_questions + 1)])
            model_desc += f"S{symptom_id} =~ {questions_desc}\n"
        
        general_factor_desc = "G =~ " + " + ".join([f'S{i}' for i in symptom_questions_map.keys()])
        model_desc += general_factor_desc

        return model_desc

    def run(self):
        return self.fit_models()

# Example usage
if __name__ == "__main__":
    user_id = 2  # Example user ID
    modeler = UserSymptomModeler(user_id)
    results = modeler.run()

    for date, model_results in results.items():
        print(f"Date: {date}")
        for symptom, output in model_results.items():
            print(f"  {symptom}: {output}")
