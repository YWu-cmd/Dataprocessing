from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import your actual classes here
from Database import Admin, User, Question, Option, Survey, Answer, question_survey_relation

DATABASE_URL = "sqlite:///survey_system.db"  # Replace with your actual database connection string
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


# 问题列表
questions_v1 = [
    "我在想到家庭的时候感到沮丧或愤怒",
    "我非常的害羞，不喜欢与人交流",
    "我会无缘无故的心跳加速",
    "我无法控制自己的食欲",
    "我不像以前那样喜欢与人打交道了",
    "我感到孤独寂寞",
    "我的家人让我心烦意乱",
    "我无法控制的想吃东西",
    "我担心我在公共场合会发生惊恐",
    "我有信心我会在学业上取得让自己满意的结果",
    "我存在睡眠障碍",
    "我常常胡思乱想",
    "我觉得自己一无是处",
    "总的来说我有一个幸福的家庭",
    "我觉得自己很无助",
    "我吃太多东西了",
    "我沉迷于游戏/短视频",
    "我常感受到恐惧或惊慌",
    "当我不能玩游戏/浏览短视频时会感到沮丧，烦躁，焦虑",
    "我常常感到紧张",
    "我很难控制自己的情绪",
    "我很擅长交朋友",
    "我有时想摔或者砸东西",
    "我时常感到苦闷",
    "我常常担心周围的人不喜欢我",
    "我希望我的家庭更加和睦",
    "我很容易发脾气",
    "当周围有陌生人时我感到不适",
    "会想到死亡的事",
    "我是一个比较有自知之明的人",
    "因为玩游戏/刷视频，我减少了参与其他活动的时间",
    "我无法像以前一样集中注意力",
    "我很难在课堂中保持积极性",
    "因为游戏/短视频，我做过让自己后悔的事",
    "我常常节食",
    "我无法很好的完成学业",
    "我通过游戏/短视频来逃避一些现实中的问题",
    "我有想打人或伤害他人的冲动",
    "对事物不感兴趣",
    "感到神经过敏，心中不踏实",
    "想过结束自己的生命",
    "我认为没有人理解我",
    "我常常与人发生争执",
    "我喜欢我自己",
]

def create_survey_with_questions(questions):
    session = Session()
    try:
        new_survey = Survey(survey_name="心理健康调查", survey_description="关于心理健康状态的调查", q_nums=len(questions))
        session.add(new_survey)
        session.flush()  # This will assign an ID to new_survey without committing the transaction

        for question_text in questions:
            new_question = Question(question_description=question_text)
            session.add(new_question)
            session.flush()  # Assign an ID to new_question without committing the transaction
            # Add to association table
            assoc = question_survey_relation.insert().values(question_id=new_question.question_id, survey_id=new_survey.survey_id)
            session.execute(assoc)  # Use session.execute instead of engine.execute

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    create_survey_with_questions(questions_v1)
