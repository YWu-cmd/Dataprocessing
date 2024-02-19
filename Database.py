from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# Association Table for Many-to-Many relationship between Question and Survey
question_survey_relation = Table('question_survey_relation', Base.metadata,
    Column('qsr_id', Integer, primary_key=True, autoincrement=True),
    Column('question_id', Integer, ForeignKey('question.question_id')),
    Column('survey_id', Integer, ForeignKey('survey.survey_id')),
    Column('order', Integer)
)
# 定义症状与问题之间的关联表
symptom_question_relation = Table('symptom_question_relation', Base.metadata,
    Column('symptom_id', Integer, ForeignKey('symptom.symptom_id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('question.question_id'), primary_key=True)
)


class Admin(Base):
    __tablename__ = 'admin'
    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    wechatID = Column(String, unique=True)

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    wechatID = Column(String, unique=True)
    name = Column(String)
    birthday = Column(DateTime)

class Question(Base):
    __tablename__ = 'question'
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    question_description = Column(String)
    question_type = Column(String)

class Option(Base):
    __tablename__ = 'option'
    question_id = Column(Integer, ForeignKey('question.question_id'), primary_key=True)
    option_id = Column(Integer, primary_key=True)  # This is part of the composite key, not a unique key by itself
    option_name = Column(String, nullable=False)


class Survey(Base):
    __tablename__ = 'survey'
    survey_id = Column(Integer, primary_key=True, autoincrement=True)
    q_nums = Column(Integer)
    survey_name = Column(String)
    survey_description = Column(String)
    questions = relationship('Question', secondary=question_survey_relation, backref='surveys')

class Answer(Base):
    __tablename__ = 'answer'
    answer_id = Column(Integer, primary_key=True, autoincrement=True)
    qsr_id = Column(Integer, ForeignKey('question_survey_relation.qsr_id'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    option_id = Column(Integer, ForeignKey('option.option_id'))
    create_date = Column(DateTime, default=datetime.utcnow)
    test_duration = Column(Integer)
    
class Symptom(Base):
    __tablename__ = 'symptom'
    symptom_id = Column(Integer, primary_key=True, autoincrement=True)
    symptom_name = Column(String, nullable=False)
    
    # 使用 relationship 建立与 Question 的多对多关系
    questions = relationship("Question",
                             secondary=symptom_question_relation,
                             backref="symptoms")

class Score(Base):
    __tablename__ = 'score'
    score_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    attempt_id = Column(Integer, nullable=False)
    symptom_id = Column(Integer, ForeignKey('symptom.symptom_id'), nullable=False)
    score = Column(Integer, nullable=False)

    # 建立与 User 和 Symptom 的关系
    user = relationship("User", backref="scores")
    symptom = relationship("Symptom", backref="scores")


# Replace the SQLite URL with your actual database connection string
engine = create_engine('sqlite:///survey_system.db', echo=True)

Base.metadata.create_all(engine)
