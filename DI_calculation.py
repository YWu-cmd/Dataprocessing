import pandas as pd
from semopy import Model
from semopy.inspector import inspect

class DICalculation:
    def __init__(self, data_path, symptom_to_questions):
        self.data_path = data_path
        self.symptom_to_questions = symptom_to_questions  # Now part of the object
        self.data = None
        self.model = None
        self.results = None

    def load_data(self):
        self.data = pd.read_csv(self.data_path).iloc[:, 1:]
        return self.data

    def define_model(self):
        model_desc = "G =~ "
        model_desc += " + ".join([f"S{symptom}_{qsr}" for symptom, qsrs in self.symptom_to_questions.items() for qsr in qsrs])
        
        for symptom, qsrs in self.symptom_to_questions.items():
            specific_factor = f"S{symptom} =~ " + " + ".join([f"S{symptom}_{qsr}" for qsr in qsrs])
            model_desc += "\n" + specific_factor
        return model_desc

    def build_model(self, model_description):
        self.model = Model(model_description)

    def fit_model(self):
        self.results = self.model.fit(self.data)
        return self.results

    def get_estimates(self):
        return inspect(self.model)
    
    def calculate_scores(self):
        estimates = inspect(self.model)
        
        # Initialize columns for scores to 0
        for symptom in self.symptom_to_questions:
            self.data[f'Score_S{symptom}'] = 0
        
        self.data['DI_score'] = 0
        
        # Step 1: Calculate scores for each S{symptom}
        for symptom, qsrs in self.symptom_to_questions.items():
            for qsr in qsrs:
                estimate_row = estimates.loc[(estimates['lval'] == f'S{symptom}_{qsr}') & (estimates['rval'] == f'S{symptom}')]
                if not estimate_row.empty:
                    estimate = estimate_row['Estimate'].values[0]
                    self.data[f'Score_S{symptom}'] += estimate * self.data[f'S{symptom}_{qsr}']
        
        # Step 2: Calculate score for G using scores from Step 1
        for symptom in self.symptom_to_questions:
            estimate_row = estimates.loc[(estimates['lval'] == f'S{symptom}') & (estimates['rval'] == 'G')]
            if not estimate_row.empty:
                estimate = estimate_row['Estimate'].values[0]
                self.data['DI_score'] += estimate * self.data[f'Score_S{symptom}']
                print(f"DI Score Contribution from Symptom {symptom}, Estimate: {estimate}, lval: {estimate_row['lval'].values[0]}, rval: {estimate_row['rval'].values[0]}, op: {estimate_row['op'].values[0]}")

        

# Usage
if __name__ == "__main__":
    data_path = 'survey_earliest_answers.csv'
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
    
    builder = DICalculation(data_path, symptom_to_questions)
    df = builder.load_data()
    
    model_description = builder.define_model()
    builder.build_model(model_description)
    
    builder.fit_model()
    builder.calculate_scores()  # Calculate scores after fitting the model
    
    if 'DI_score' in builder.data.columns:
        print(builder.data[['DI_score']])
    else:
        print("DI_score column not found. Ensure calculate_scores method is correctly implemented.")
