from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database import Symptom, Question, symptom_question_relation  # Corrected import statement

# Database connection setup
DATABASE_URL = "sqlite:///survey_system.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Symptoms and their related question IDs
symptom_to_questions = {
    "抑郁症": [6, 11, 13, 24, 39],
    "广泛性焦虑": [3, 9, 11, 12, 18, 20, 15, 32, 40],
    "社交焦虑": [2, 5, 11, 22, 25, 28, 30],
    "学业困境": [10, 33, 36],
    "饮食问题": [4, 8, 16],
    "沮丧": [21, 23, 27, 35, 42, 43 ,44],
    "家庭困境": [1, 7, 14, 26],
    "娱乐成瘾": [17, 19, 31, 34, 37],
    "SI": [29, 41],
    "HI": [38, 23, 29],
    "DI": [42, 44]
}

def insert_symptoms_and_questions():
    session = Session()
    try:
        for symptom_name, question_ids in symptom_to_questions.items():
            # 查找或创建症状
            symptom = session.query(Symptom).filter_by(symptom_name=symptom_name).first()
            if not symptom:
                symptom = Symptom(symptom_name=symptom_name)
                session.add(symptom)
                session.flush()  # 确保symptom_id生成

            # 关联症状和问题
            for question_id in question_ids:
                question = session.query(Question).filter_by(question_id=question_id).first()
                if question and question not in symptom.questions:
                    symptom.questions.append(question)
            
            session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    insert_symptoms_and_questions()
