from reportlab.lib.pagesizes import letter
import matplotlib as mpl
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import numpy as np
import os
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
# Import your data analysis module and SQLAlchemy models
from fetch_percentile_score import SurveyAnalysis  # Adjust as necessary
from Database import User, Score, Symptom, Question, Answer, symptom_question_relation, question_survey_relation  # Adjust the import path as necessary
from sqlalchemy import func  # Import func here

# 注册字体

pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))

class CCAPSReportGenerator:

    def __init__(self, user_id, db_url='sqlite:///survey_system.db'):
        self.user_id = user_id
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.analysis = SurveyAnalysis(db_url)
        self.doc = SimpleDocTemplate(f"CCAPS_44_Report_{user_id}.pdf", pagesize=letter)
        self.styles = getSampleStyleSheet()

    def fetch_data(self):
        session = self.Session()

        # Fetch basic information of the user
        user_info = session.query(User).filter(User.user_id == self.user_id).one()

        # Fetch all attempts by the user
        attempts = session.query(Score).filter(Score.user_id == self.user_id).order_by(Score.attempt_id).all()

        # Organize scores by attempt and symptom
        attempts_scores = {}
        for attempt in attempts:
            if attempt.attempt_id not in attempts_scores:
                attempts_scores[attempt.attempt_id] = {}
            symptom_name = session.query(Symptom.symptom_name).filter(Symptom.symptom_id == attempt.symptom_id).scalar()
            attempts_scores[attempt.attempt_id][symptom_name] = attempt.score

        self.user_data = {
            'name': user_info.name,
            'birthday': user_info.birthday,
            'attempts_scores': attempts_scores
        }

    def fetch_additional_data(self):
        session = self.Session()
        try:
            # Attempt to fetch data with an explicit join path
            data = session.query(Question.question_id, 
                                Symptom.symptom_name, 
                                Question.question_description, 
                                Answer.option_id)\
                        .join(symptom_question_relation, Symptom.symptom_id == symptom_question_relation.c.symptom_id)\
                        .join(Question, Question.question_id == symptom_question_relation.c.question_id)\
                        .join(question_survey_relation, Question.question_id == question_survey_relation.c.question_id)\
                        .join(Answer, Answer.qsr_id == question_survey_relation.c.qsr_id)\
                        .filter(question_survey_relation.c.survey_id == 1)\
                        .order_by(Symptom.symptom_id, Question.question_id).all()
                        
            # Process fetched data
            organized_data = []
            for d in data:
                question_id, symptom_name, question_description, option_id = d
                organized_data.append({
                    'question_id': question_id,
                    'symptom_name': symptom_name,
                    'question_description': question_description,
                    'option_id': option_id
                })
            return organized_data
        except Exception as e:
            print(f"Error in fetch_additional_data: {e}")
        finally:
            session.close()





    def fetch_symptom_names(self):
        session = self.Session()  # Assuming self.Session() is already defined and returns a SQLAlchemy session
        symptom_names_dict = {}
        try:
            symptoms = session.query(Symptom.symptom_id, Symptom.symptom_name).all()
            symptom_names_dict = {symptom.symptom_id: symptom.symptom_name for symptom in symptoms}
        except Exception as e:
            print(f"Error fetching symptom names: {e}")
        finally:
            session.close()
        return symptom_names_dict
    
    def get_color_ranges(self):
        color_ranges = {
            1: [(0, 15, "white"), (15, 38, "yellow"), (38, 100, "pink")],
            2: [(0, 19, "white"), (19, 39, "yellow"), (39, 100, "pink")],
            3: [(0, 17, "white"), (17, 56, "yellow"), (56, 100, "pink")],
            4: [(0, 18, "white"), (18, 54, "yellow"), (54, 100, "pink")],
            5: [(0, 43, "white"), (43, 59, "yellow"), (59, 100, "pink")],
            6: [(0, 49, "white"), (49, 57, "yellow"), (57, 100, "pink")],
            7: [(0, 61, "white"), (61, 69, "yellow"), (69, 100, "pink")],
            8: [(0, 57, "white"), (57, 69, "yellow"), (69, 100, "pink")],
            9: [(0, 12, "white")],  # SI
            10: [(0, 12, "grey")]  # HI
        }
        return color_ranges

    def build_symptom_plots_data(self, combined_data):
        symptom_plots_data = {}
        for attempt in combined_data:
            attempt_date = attempt['attempt_date']
            for symptom_id, score_info in attempt['symptom_scores'].items():
                if symptom_id not in symptom_plots_data:
                    symptom_plots_data[symptom_id] = {'dates': [], 'percentiles': [], 'scores': []}
                symptom_plots_data[symptom_id]['dates'].append(attempt_date)
                if 'percentile' in score_info:
                    symptom_plots_data[symptom_id]['percentiles'].append(score_info['percentile'])
                symptom_plots_data[symptom_id]['scores'].append(score_info['score'])
        return symptom_plots_data


    def student_info(self):
        # 设置字体
        style = getSampleStyleSheet()['Normal']
        style.fontName = 'SimHei'
        style.fontSize = 10  # 可以调整字体大小
        
        # 获取最新尝试的日期
        latest_attempt_date = max(self.user_data['attempts_scores'].keys())
        
        # 创建表格数据
        data = [['姓名', '生日', '填写日期'],
                [self.user_data['name'], self.user_data['birthday'].strftime("%Y-%m-%d"), latest_attempt_date]]
        
        # 创建表格
        table = Table(data, colWidths=[7*cm, 7*cm, 7*cm], rowHeights=1*cm)  # 可以调整宽度和高度
        
        # 设置表格样式
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),  # 设置表格字体
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # 设置字体大小
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),  # 设置标题背景色
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # 居中对齐
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),  # 垂直居中
        ]))
        
        return table



    def generate_plots(self):
        mpl.rcParams['font.sans-serif'] = ['SimHei']
        mpl.rcParams['axes.unicode_minus'] = False

        combined_data = self.analysis.calculate_scores_and_percentiles(self.user_id)
        symptom_names_dict = self.fetch_symptom_names()

        color_ranges = self.get_color_ranges()  # 获取颜色范围
        symptom_plots_data = self.build_symptom_plots_data(combined_data)  # 构建数据

        # Initialize figure and GridSpec layout for plotting
        fig = plt.figure(figsize=(20, 10), tight_layout=True)
        gs = GridSpec(2, 9, figure=fig, wspace=0)  # Configure for 1 row, 8 columns, no horizontal space

        # Plotting symptoms with their percentiles
        # Plotting the first 8 symptoms
        for i, (symptom_id, data) in enumerate(sorted(symptom_plots_data.items(), key=lambda x: x[0])[:8]):
            ax = fig.add_subplot(gs[:, i])
            for low, high, color in color_ranges.get(symptom_id, []):
                ax.axhspan(low, high, facecolor=color, alpha=0.5)
            ax.plot(data['dates'], data['percentiles'], marker='o', linestyle='-', color='blue')
            ax.set_title(symptom_names_dict.get(symptom_id, f"Symptom {symptom_id}"), fontsize=10)
            ax.set_ylim(0, 100)
            ax.set_xticks([])
            ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
            if i == 0:
                ax.set_ylabel('← 百分比得分 →', labelpad=20)
            else:
                ax.yaxis.set_visible(False)

        # Additional plotting for SI and HI in the 9th column
        # SI subplot
        ax_si = fig.add_subplot(gs[0, -1])  # Top half of the 9th column for SI
        si_data = symptom_plots_data.get(9, {'dates': [], 'scores': []})  # Fetch SI data
        for low, high, color in color_ranges.get(9, [(0, 12, "white")]):
            ax_si.axhspan(low, high, facecolor=color, alpha=0.5)
        ax_si.plot(si_data['dates'], si_data['scores'], marker='o', linestyle='-', color='blue')
        ax_si.set_title(symptom_names_dict.get(9, "SI"), fontsize=10)
        ax_si.set_ylim(0, 12)
        ax_si.set_xticks([])  # Remove x-axis labels
        ax_si.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

        # HI subplot adjustments
        ax_hi = fig.add_subplot(gs[1, -1])  # Bottom half of the 9th column for HI
        hi_data = symptom_plots_data.get(10, {'dates': [], 'scores': []})  # Fetch HI data
        for low, high, color in color_ranges.get(10, [(0, 12, "grey")]):
            ax_hi.axhspan(low, high, facecolor=color, alpha=0.5)
        ax_hi.plot(hi_data['dates'], hi_data['scores'], marker='o', linestyle='-', color='blue')
        ax_hi.set_title(symptom_names_dict.get(10, "HI"), fontsize=10)
        ax_hi.set_ylim(0, 12)
        ax_hi.set_xticks([])  # Remove x-axis labels
        ax_hi.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

        return fig




    def create_table_plot(self):
        # Placeholder for fetching data
    # Placeholder for fetching data
        combined_data = self.analysis.calculate_scores_and_percentiles(self.user_id)
        symptom_names_dict = self.fetch_symptom_names()
        symptom_plots_data = self.build_symptom_plots_data(combined_data)
        color_ranges = self.get_color_ranges()

        # Sort dates, get the latest 20
        all_dates = sorted(set(symptom_plots_data[1]['dates']), reverse=False)
# Decide the number of dates to display, ensuring we don't exceed the available dates
        num_dates_to_display = min(20, len(all_dates))

    # Assuming all_dates is already sorted from earliest to latest
        earliest_date = [all_dates[0]]  # Get the earliest date
        latest_dates = all_dates[-19:]  # Get the latest 19 dates

        # Combine them, ensuring the earliest date is first
        combined_dates = earliest_date + latest_dates

        # Initialize table data without a header row
        table_data = []

        # Populate table data with combined dates
        for idx, date in enumerate(combined_dates):
            # Marking the first entry as "基准" (baseline) and the last entry as "最新" (latest)
            if idx == 0:
                date_mark = f"{date} (基准)"
            elif idx == len(combined_dates) - 1:
                date_mark = f"{date} (最新)"
            else:
                date_mark = date

            row = [date_mark]
            for symptom_id in range(1, 11):
                data = symptom_plots_data[symptom_id]
                if date in data['dates']:
                    index = data['dates'].index(date)
                    score = data['percentiles'][index] if symptom_id <= 8 else data['scores'][index]
                    row.append(f"{score:.2f}")
                else:
                    row.append("N/A")
            table_data.append(row)

        # Create figure for the table
        fig, ax = plt.subplots(figsize=(20, 4),tight_layout=True)
        ax.axis('tight')
        ax.axis('off')

        # Create table with specified column widths
        colWidths = [2.22/len(table_data[0])] * 9 + [1.11/len(table_data[0])] * 2
        table = ax.table(cellText=table_data, cellLoc='center', loc='center', colWidths=colWidths)

        # Apply colors based on your color_ranges logic
        for i, row in enumerate(table_data[1:], start=1):  # Skip header row
            for j, cell_value in enumerate(row[1:], start=1):  # Skip date column for coloring
                if j <= 10:  # Symptom 1-8, color based on percentile
                    color = "white"  # Default color
                    for low, high, color_code in color_ranges[j]:
                        if low <= float(cell_value) <= high:
                            color = color_code
                            break
                    table.get_celld()[(i, j)].set_facecolor(color)
                # Additional logic for symptoms 9-10 if necessary

        # Adjust layout
        plt.tight_layout()

        # Save the plot as an image
        fig_path = "symptom_table_plot.png"
        plt.savefig(fig_path, bbox_inches='tight', dpi=300)
        plt.close(fig)

        return fig_path



    def fetch_latest_attempt_data(self):
        session = self.Session()

        # Fetch the latest attempt date for a specific user
        latest_attempt_date = session.query(func.max(Answer.create_date))\
                                    .filter(Answer.user_id == self.user_id)\
                                    .scalar()

        # Fetch additional data for the latest attempt, properly joining tables
        additional_data = session.query(
            Symptom.symptom_id,
            Symptom.symptom_name,
            Question.question_id,
            Question.question_description,
            Answer.option_id
        ).join(symptom_question_relation, Symptom.symptom_id == symptom_question_relation.c.symptom_id)\
        .join(Question, Question.question_id == symptom_question_relation.c.question_id)\
        .join(question_survey_relation, Question.question_id == question_survey_relation.c.question_id)\
        .join(Answer, Answer.qsr_id == question_survey_relation.c.qsr_id)\
        .filter(Answer.create_date == latest_attempt_date, Answer.user_id == self.user_id)\
        .all()

        session.close()  # Close the session
        return additional_data

    def create_latest_attempt_results(self):
        import matplotlib.pyplot as plt  # Ensure matplotlib is imported

        additional_data = self.fetch_latest_attempt_data()

        # Process data to calculate the table structure, correctly including all questions for the first eight symptoms
        symptom_to_questions = {}
        unique_symptoms_collected = set()  # To track unique symptoms processed

        for symptom_id, symptom_name, question_id, question_description, option_id in additional_data:
            if symptom_id not in symptom_to_questions:
                if len(unique_symptoms_collected) < 8:
                    unique_symptoms_collected.add(symptom_id)
                    symptom_to_questions[symptom_id] = {"symptom_name": symptom_name, "questions": []}
                else:
                    # Skip further processing if we already have eight unique symptoms
                    continue

            # This ensures questions for the eighth symptom are also included
            if symptom_id in unique_symptoms_collected:
                symptom_to_questions[symptom_id]["questions"].append((question_id, question_description, option_id))

        # Preparing data for visualization
        table_data = []
        for symptom, details in symptom_to_questions.items():
            table_data.append(["", f"{details['symptom_name']}", ""])  # Symptom row
            for question in details["questions"]:
                table_data.append([question[0], question[1], question[2]])  # Question rows

        # Calculate the split point for the data
        split_point = round(len(table_data) / 2)
        first_half_data = table_data[:split_point]
        second_half_data = table_data[split_point:]

        # Ensure both halves have the same number of rows for a symmetrical table
        while len(first_half_data) < len(second_half_data):
            first_half_data.append(["", "", ""])  # Add empty rows to the first half if needed

        # Merge the two halves into a single table structure
        merged_table_data = []
        for row_index in range(max(len(first_half_data), len(second_half_data))):
            # If one half is shorter, add empty cells for missing data
            first_half_row = first_half_data[row_index] if row_index < len(first_half_data) else ["", "", ""]
            second_half_row = second_half_data[row_index] if row_index < len(second_half_data) else ["", "", ""]
            merged_table_data.append(first_half_row + second_half_row)

        # Visualization with six columns
        fig, ax = plt.subplots(figsize=(20, max(len(first_half_data), len(second_half_data)) / 4))
        ax.axis('off')

        table = ax.table(
            cellText=merged_table_data,
            cellLoc='center',
            loc='center',
            colWidths=[0.1, 0.3, 0.1, 0.1, 0.3, 0.1]  # Adjusted for six columns
        )

        plt.tight_layout()
        fig_path = "latest_attempt_table.png"
        plt.savefig(fig_path, bbox_inches="tight")
        plt.close(fig)

        return fig_path





    def build_report(self):
        pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
        mpl.rcParams['font.sans-serif'] = ['SimHei']  # 使用 SimHei 字体
        mpl.rcParams['axes.unicode_minus'] = False  # 支持中文字体中的负号

        # 设置中文样式
        style = getSampleStyleSheet()
        chinese_style = ParagraphStyle('ChineseStyle', parent=style['Normal'], fontName='SimHei', fontSize=12)

        # 初始化 ReportLab Story
        story = []
        
        # 添加标题
        title = "CCAPS个人报告"
        story.append(Paragraph(title, chinese_style))
        story.append(Spacer(1, 12))

        # Part 1: 学生信息
        info_table = self.student_info()
        story.append(info_table)
        story.append(Spacer(1, 12))

        # Part 2: 症状图表
        fig = self.generate_plots()
        fig_path = "plot.png"
        fig.savefig(fig_path, bbox_inches='tight', dpi=150)  # 保存图表，调整 dpi 以控制文件大小
        story.append(Image(fig_path, width=6*inch, height=2*inch))  # 调整图像尺寸

        # Part 3: 分数表格
        scores_table = self.create_table_plot()
        fig_path = "symptom_table_plot.png"
        story.append(Image(fig_path, width=6*inch, height=2*inch))  # 调整图像尺寸

        # Part 4: 最新尝试结果
        latest_attempt_table = self.create_latest_attempt_results()
        fig_path = "latest_attempt_table.png"
        story.append(Image(fig_path, width=6*inch, height=2*inch))  # 调整图像尺寸

        # 构建 PDF 文档
        self.doc.build(story)


    def run(self):
        """Execute the report generation process."""
        self.fetch_data()
        self.generate_plots()
        self.build_report()
        self.create_table_plot()

if __name__ == "__main__":
    user_id = 4  # Example user_id, replace with the actual user ID you want to generate a report for
    report_generator = CCAPSReportGenerator(user_id)
    report_generator.run()
