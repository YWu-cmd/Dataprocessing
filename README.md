#Database.py
文件定义了一个调查系统的数据库模型，这包括用户（User）、管理员（Admin）、问题（Question）、选项（Option）、调查（Survey）、答案（Answer）、症状（Symptom）、分数（Score）以及两个关联表来处理多对多关系：问题与调查之间的关系（question_survey_relation），以及症状与问题之间的关系（symptom_question_relation）。这些模型使用SQLAlchemy ORM定义，可用于Python中与数据库的交互。以下是每个部分的简要说明：

关联表
question_survey_relation: 用于建立问题和调查之间多对多的关系。每个记录关联一个问题和一个调查，还包括问题在调查中的顺序。
symptom_question_relation: 用于建立症状和问题之间多对多的关系。这允许将特定的问题与一个或多个症状关联。
数据模型
Admin: 表示系统管理员，包含唯一的微信ID。
User: 表示系统用户，同样包含唯一的微信ID以及用户的姓名和生日。
Question: 定义调查中的问题，包含问题描述和类型。
Option: 定义问题的选项，与问题是多对一的关系。
Survey: 表示一份调查，包含调查的名称、描述和包含的问题列表。问题通过question_survey_relation与调查建立关系。
Answer: 用户的答案记录，包括选择的选项、用户ID、问题调查关系ID等。
Symptom: 定义症状，可以通过symptom_question_relation与问题建立多对多的关系。
Score: 记录用户在某次尝试中对于特定症状的得分。
数据库创建和初始化
在文件的末尾，使用create_engine创建一个SQLite数据库引擎，并通过Base.metadata.create_all(engine)创建所有定义的表结构。这一步是整个数据库初始化过程的关键，确保所有的表和关系都被正确创建于数据库中。

使用示例
要使用这个模型与数据库进行交互，可以创建另一个Python脚本，导入这些模型，并通过SQLAlchemy的Session进行数据的增删查改操作。例如，添加一个新用户、创建一项调查、记录用户的答案等。
# 数据准备脚本使用指南

为了进行有效的数据统计和图表生成，本项目提供了一系列脚本，用于在数据库中预先生成必要的数据。这些脚本包括`option_generator`、`score_generator`、`survey_generator`和`student_records_generator`，它们分别负责创建调查选项、生成用户分数、创建调查及问题和生成学生记录。以下是如何使用这些脚本的详细指南。

## 脚本概览

- **option_generator**: 生成调查问题的回答选项。
- **score_generator**: 为用户生成特定症状的分数记录。
- **survey_generator**: 创建新的调查，并为其添加问题。
- **student_records_generator**: 生成模拟的学生用户及其答案记录。

## 环境要求

- Python 3.x
- SQLAlchemy

请确保您已安装Python及上述依赖包。

## 安装依赖

```bash
pip install sqlalchemy
```

## 使用流程

### 1. 生成调查选项（option_generator）

在创建调查问题后，运行`option_generator`脚本为每个问题生成预定义的选项，如“完全不像我”到“非常像我”。

```python
# option_generator.py
from option_generator import create_options_for_questions

create_options_for_questions()
```

### 2. 生成用户分数（score_generator）

使用`score_generator`脚本为数据库中的用户生成症状分数，这些分数后续将用于数据统计和图表生成。

```python
# score_generator.py
from score_generator import generate_scores_for_users

generate_scores_for_users()
```

### 3. 创建调查及问题（survey_generator）

运行`survey_generator`脚本创建新的调查，并为其添加一系列问题。这些问题将作为调查的一部分供用户回答。

```python
# survey_generator.py
from survey_generator import create_survey_with_questions

questions = [
    "我在想到家庭的时候感到沮丧或愤怒",
    # 添加更多问题...
]

create_survey_with_questions(questions)
```

### 4. 生成学生记录（student_records_generator）

最后，使用`student_records_generator`脚本生成模拟的学生记录，包括学生基本信息和他们对调查问题的答案。

```python
# student_records_generator.py
from student_records_generator import generate_student_answers

generate_student_answers()
```

## 运行顺序

为确保数据的完整性和逻辑一致性，请按以下顺序运行脚本：

1. **option_generator**
2. **survey_generator**
3. **score_generator**
4. **student_records_generator**

这将确保在生成用户答案和分数前，调查问题和选项已经准备好。

## 贡献与支持

欢迎通过提交问题、请求新功能或贡献代码的方式来参与本项目。如果在使用脚本过程中遇到任何问题，也欢迎在项目的Issues区域提出。

## 许可证

本项目使用MIT许可证，更多详情请查看LICENSE文件。

我们期待您的参与，共同改进本项目，以更好地服务于数据统计和图表生成的需求。
对于 fetch_percentile_score.py
假设我们已经有一个调查系统数据库，包含用户(User)、分数(Score)和症状(Symptom)等表。我们想要分析特定用户的调查结果，包括计算其对每个症状的分数以及这些分数的百分位数（对于症状ID小于等于8的情况）。以下是如何使用这段代码的示例：

### 步骤1：确保数据库和模型准备就绪

首先，确保`Database.py`文件中定义了`User`、`Score`和`Symptom`模型，并且这些模型与数据库中的表相匹配。例如：

```python
# Database.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    birthday = Column(DateTime)

class Score(Base):
    __tablename__ = 'scores'
    score_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    symptom_id = Column(Integer)
    attempt_id = Column(String)
    score = Column(Float)

class Symptom(Base):
    __tablename__ = 'symptoms'
    symptom_id = Column(Integer, primary_key=True)
    name = Column(String)
```

### 步骤2：运行分析

接下来，假设我们要分析用户ID为1的调查结果，我们可以在Python脚本中这样做：

```python
# 假设以上代码片段保存在SurveyAnalysis.py中
from SurveyAnalysis import SurveyAnalysis

# 用户ID，这个值应该基于实际需要动态替换
user_id = 1

# 创建SurveyAnalysis实例
analysis = SurveyAnalysis()

# 计算并获取用户ID为1的用户的调查结果
results = analysis.calculate_scores_and_percentiles(user_id)

# 打印结果
analysis.print_results(results)
```

### 输出示例

当运行上述代码时，控制台将输出类似以下格式的信息，展示了用户ID为1的用户在每次尝试中对每个症状的分数和百分位数（如果适用）：

```plaintext
{
  'name': 'John Doe',
  'birthday': '1990-01-01',
  'attempt_date': '2023-04-01',
  'symptom_scores': {
    1: {'score': 8.5, 'percentile': 75.00},
    2: {'score': 7.0},
    ...
  }
},
...
```

这个输出表明，对于用户John Doe，他在2023年4月1日的尝试中，对于症状1的分数是8.5，处于所有参与者中的75百分位；对于症状2的分数是7.0，由于症状ID大于8，所以没有计算百分位数。

通过这种方式，我们可以为每个用户提供详细的调查分析结果，帮助理解他们的反馈及其在群体中的相对位置。

# CCAPS_report.py


## 主要功能

- 从数据库中提取用户的基本信息和调查结果。
- 分析用户调查数据，包括计算分数和百分位数。
- 生成包括文本、表格和图表的PDF格式个人报告。
- 支持中文字符，适用于需要中文报告的场景。

## 环境要求

- Python 3.x
- SQLAlchemy
- matplotlib
- reportlab

请确保安装了所有必要的Python依赖库。

## 安装依赖

使用pip安装所需的依赖：

```bash
pip install sqlalchemy matplotlib reportlab
```

## 快速开始

1. 确保您的数据库已经设置，并且`Database.py`和`fetch_percentile_score.py`（根据您的实际文件调整名称）正确导入和配置。

2. 将`SimHei.ttf`字体文件放置在脚本相同的目录下，以确保中文在PDF报告中的正确显示。

3. 修改脚本中的`user_id`和`db_url`（如果需要）以匹配您的数据库和目标用户。

### 示例代码

```python
from CCAPS import CCAPSReportGenerator

# 设置目标用户ID和数据库URL
user_id = 4  # 替换为目标用户ID
db_url = 'sqlite:///survey_system.db'  # 替换为实际的数据库连接字符串

# 创建报告生成器实例
report_generator = CCAPSReportGenerator(user_id, db_url)

# 生成报告
report_generator.run()
```

此脚本将生成一个名为`CCAPS_44_Report_[user_id].pdf`的PDF文件，其中`[user_id]`是您在脚本中指定的用户ID。

## 报告内容

生成的PDF报告将包括以下部分：

- **学生信息**：显示用户的姓名、生日和最新填写日期。
- **症状图表**：展示用户对每个症状的分数和百分位数变化趋势。
- **分数表格**：详细列出用户在每次尝试中的分数。
- **最新尝试结果**：展示用户在最新一次调查尝试中的答案和分数。
