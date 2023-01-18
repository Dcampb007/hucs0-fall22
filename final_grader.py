import pandas as pd
import sys
import math
from hashlib import md5

# Constants
kRequiredExamScoreToNotTakeFinal = 0.90
kExam1 = 'Exam 1'
kExam2 = 'Exam 2'
kFinalExam = 'Final Exam'
kExams = 'Exams'
kHWs = 'HWs'
kQuizzes = 'Quizzes'
kProjects = 'Projects'
kLab = 'Lab'
kAssignmentsToIgnore = {}

num_students_not_taking_final = 0
num_students_taking_final = 0
num_students_failing = 0
# Map from
# letter grade -> [num_students_with_letter_grade, percentage_of_students_with_letter_grade]
num_students_per_grade = {'A': [0,0], 'B': [0,0], 'C': [0,0], 'D': [0,0], 'F': [0,0], 'INC': [0,0]}

# Add students that should have an Incomplete here
kStudentsWithIncompletes = {
    'aff4e6781a23832670f7384495a402b0',
    'dd0b27ae1a198676a19a2c2374d17db6',
    '7ab9463954813c4b7dfcb7a323262781',
    '1c9e50d452aa05bdf3023a5c6ba87cbb',
    '72e178e60036e7a3e42d7d14f7fb32b7',
    '1d706039ee9a3e0d2771e323f6277ce5',
}


# If True, output will be keyed by md5 hash value. If False, output will be keyed by student
# Bison ID number. set STUDENT_MODE = False to produce output to be entered into bisonweb.
STUDENT_MODE = False


def GetOutputHeaders():
    if STUDENT_MODE:
        return {0: 'Final Letter Grade'}
    else:
        return {0: 'First Name', 1: 'Last Name', 2:'Final Grade Percentage', 3: 'Final Letter Grade'}


def GetLetterGrade(student_id, final_grade):
    if student_id in kStudentsWithIncompletes:
        return 'INC'
    elif final_grade >= 90:
        return 'A'
    elif final_grade >= 80:
        return 'B'
    elif final_grade >= 70:
        return 'C'
    elif final_grade >= 60:
        return 'D'
    else:
        return 'F'

# Gets the max score for each assignment and assignment type


def GetAssignmentNamesToMaxScores(section_df):
    assignment_name_to_max_score = {
        kHWs: {}, kQuizzes: {}, kExams: {}, kProjects: {}}
    for col in range(len(section_df.iloc[2])):
        cell_val = section_df.iloc[2][col]
        if (cell_val.startswith(('HW', kLab))):
            assignment_name_to_max_score[kHWs][cell_val] = section_df.iloc[0][col]
        elif (cell_val.startswith('Quiz')):
            assignment_name_to_max_score[kQuizzes][cell_val] = section_df.iloc[0][col]
        elif (cell_val.startswith('Project')):
            assignment_name_to_max_score[kProjects][cell_val] = section_df.iloc[0][col]
        elif (cell_val.startswith((kExam1, kExam2, kFinalExam))):
            assignment_name_to_max_score[kExams][cell_val] = section_df.iloc[0][col]
    return assignment_name_to_max_score

# Returns a decimal value between (0,1) that represents the students
# Quiz score.


def GetQuizSubscore(quiz_name_to_max_score, student_row):
    student_points = max_points = 0.0
    lowest_quiz_score = ('', float('inf'))
    second_lowest_quiz_score = ('', float('inf'))
    for quiz_name, max_quiz_points in quiz_name_to_max_score.items():
        if quiz_name in kAssignmentsToIgnore:
            continue

        quiz_points = student_row[quiz_name]
        student_points += quiz_points
        max_points += max_quiz_points

        quiz_score = quiz_points / max_quiz_points
        if quiz_score < lowest_quiz_score[1]:
            lowest_quiz_score = (quiz_name, quiz_score)
        elif quiz_score < second_lowest_quiz_score[1]:
            second_lowest_quiz_score = (quiz_name, quiz_score)

    # Drop First lowest quiz
    lowest_quiz = lowest_quiz_score[0]
    student_points -= student_row[lowest_quiz]
    max_points -= quiz_name_to_max_score[lowest_quiz]
    # Drop Second lowest quiz
    second_lowest_quiz = second_lowest_quiz_score[0]
    student_points -= student_row[second_lowest_quiz]
    max_points -= quiz_name_to_max_score[second_lowest_quiz]

    return student_points / max_points

# Returns a decimal value between (0,1) that represents the students
# Project score.


def GetProjectsScore(project_name_to_max_score, student_row):
    student_points = max_points = 0.0
    for project_name, max_project_points in project_name_to_max_score.items():
        if project_name in kAssignmentsToIgnore:
            continue

        project_points = student_row[project_name]
        student_points += project_points
        max_points += max_project_points

    return student_points / max_points


def GetHWLabSubscore(assignment_name_to_max_score, student_row):
    student_points = max_points = 0.0
    second_lowest_lab_score = lowest_lab_score = ('', float('inf'))

    for assignment_name, max_assignment_points in assignment_name_to_max_score.items():
        if assignment_name in kAssignmentsToIgnore:
            continue

        assignment_points = student_row[assignment_name]
        student_points += assignment_points
        max_points += max_assignment_points

        if (assignment_name.startswith(kLab)):
            lab_score = assignment_points / max_assignment_points
            if (lab_score < lowest_lab_score[1]):
                lowest_lab_score = (assignment_name, lab_score)
            elif (lab_score < second_lowest_lab_score[1]):
                second_lowest_lab_score = (assignment_name, lab_score)

        # Add extra credit to HW/Lab grades
        if assignment_name.startswith(('Pre', 'Mid', 'Post', 'Office Hours')):
            student_points += assignment_points

    # Drop first lowest
    lowest_lab = lowest_lab_score[0]
    student_points -= student_row[lowest_lab]
    max_points -= assignment_name_to_max_score[lowest_lab]
    # Drop second lowest
    second_lowest_lab = second_lowest_lab_score[0]
    student_points -= student_row[second_lowest_lab]
    max_points -= assignment_name_to_max_score[second_lowest_lab]
    return student_points / max_points


# Returns a list of decimal values between (0,1) represents the students score
# for each exam type AND a boolean that determines if the student has to take
# the final exam.
def GetExamScores(exam_name_to_max_score, student_row):
    exam1_over_90 = exam2_over_90 = False
    exam_scores = {}
    for exam_name, max_exam_points in exam_name_to_max_score.items():
        if exam_name in kAssignmentsToIgnore:
            continue

        exam_scores[exam_name] = student_row[exam_name] / max_exam_points

        # Determine if the Exam score meets the requirements to not take
        # the final.
        # This must be done BEFORE we replace kExam1 score with kExam2 score
        if exam_name == kExam1 and exam_scores[kExam1] >= kRequiredExamScoreToNotTakeFinal:
            exam1_over_90 = True
        if exam_name == kExam2 and exam_scores[kExam2] >= kRequiredExamScoreToNotTakeFinal:
            exam2_over_90 = True
    # Replace kExam1 score with kExam2 score only after we've determined if the
    # Student needs to take the kFinalExam.
    # Only replace IFF kExam2 grade > kExam1 grade
    if exam_scores[kExam2] > exam_scores[kExam1]:
        exam_scores[kExam1] = exam_scores[kExam2]

    # If student gets 90% on both kExam1 and kExam2, student automatically gets
    # 100% on Final Exam
    if exam1_over_90 and exam2_over_90:
        exam_scores[kFinalExam] = 1  # points_earned / total_points == 1
    return exam_scores, exam1_over_90 and exam2_over_90


kWeightsByTypeScheme1 = {kQuizzes: 5, kHWs: 33,
                         kProjects: 26, kExam1: 7,  kExam2: 12, kFinalExam: 17}
kWeightsByTypeScheme2 = {kQuizzes: 5, kHWs: 27,
                         kProjects: 14, kExam1: 13, kExam2: 18, kFinalExam: 23}


def GetFinalGradeForScheme(student_subscores, grading_scheme):
    max_possible = actual_achieved = 0.0
    for assignment_group_name, assignment_group_weight in grading_scheme.items():
        if assignment_group_name in kAssignmentsToIgnore:
            continue
        max_possible += assignment_group_weight
        actual_achieved += student_subscores[assignment_group_name] * \
            assignment_group_weight
    return 100 * (actual_achieved / max_possible)


def GetGradesForSection(assignment_name_to_max_score, section_df):
    global num_students_taking_final, num_students_not_taking_final, num_students_per_grade
    grades_by_hash = {}
    grades_by_bison_id = {}
    for student_row in section_df.to_dict(orient='records'):
        student_id = student_row['Public CS0 ID / Assignment']
        student_bison_id = student_row['ID Number / Assignment']
        student_bison_id = '0' + str(student_bison_id)
        student_fname = student_row['First Name']
        student_lname = student_row['Last Name']

        student_scores = {
            kQuizzes: GetQuizSubscore(assignment_name_to_max_score[kQuizzes], student_row),
            kHWs: GetHWLabSubscore(assignment_name_to_max_score[kHWs], student_row),
            kProjects: GetProjectsScore(
                assignment_name_to_max_score[kProjects], student_row)
        }
        exam_scores, exam1_exam2_over_90 = GetExamScores(
            assignment_name_to_max_score[kExams], student_row)
        student_scores.update(exam_scores)
        final_score_1 = GetFinalGradeForScheme(
            student_scores, kWeightsByTypeScheme1)
        final_score_2 = GetFinalGradeForScheme(
            student_scores, kWeightsByTypeScheme2)
        student_final_grade = math.ceil(
            round(max(final_score_1, final_score_2), 2))
        # Adjust grade for students on letter-grade border.. cuz I'm nice.
        if str(student_final_grade)[-1] == '9':
            student_final_grade+=1
        has_to_take_final = "NO" if (
            exam1_exam2_over_90 or student_final_grade >= 95) else "YES"
        student_letter_grade = GetLetterGrade(student_id, student_final_grade)
        num_students_per_grade[student_letter_grade][0] += 1
        if has_to_take_final == "NO":
            num_students_not_taking_final += 1
        else:
            num_students_taking_final += 1
        if STUDENT_MODE:
            grades_by_hash[student_id] = [student_letter_grade]
        else:
            grades_by_bison_id[student_bison_id] = [student_fname, student_lname,
                student_final_grade, student_letter_grade]

    return grades_by_hash if STUDENT_MODE else grades_by_bison_id


def GetGradesForSections(excel_file, output_file):
    # read by default 1st sheet of an excel file
    all_sheets = pd.ExcelFile(excel_file)
    assignment_name_to_max_score = None
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    for sheet_name in all_sheets.sheet_names:
        if 'Section ' in sheet_name:
            if assignment_name_to_max_score is None:
                full_sheet_no_header = pd.read_excel(
                    all_sheets, sheet_name, header=None)
                assignment_name_to_max_score = GetAssignmentNamesToMaxScores(
                    full_sheet_no_header)

            section = pd.read_excel(all_sheets, sheet_name, header=2)

            # Replace all INC and NaN with 0 to simplify functions above
            section.replace('INC', 0, inplace=True)
            section.fillna(0, inplace=True)

            grades_for_section = GetGradesForSection(
                assignment_name_to_max_score, section)
            grades_for_section_df = pd.DataFrame.from_dict(
                grades_for_section, orient='index')
            grades_for_section_df.rename(
                GetOutputHeaders(), axis='columns', inplace=True)
            grades_for_section_df.to_excel(
                writer, sheet_name='Final grades %s' % (sheet_name))
    writer.close()


def main():
    if (len(sys.argv) != 3):
        print('Please call this script with exactly two arguments, input and output file')
        return
    print('Note that all assignment names must have only the first letter capitalized (except for \'HW\') and have a space before the assignment number')
    print('')
    print('Ignoring the following assignments: ' + ','.join(kAssignmentsToIgnore) +
          '.\nTo change these, edit the script variable kAssignmentsToIgnore.')
    print("Working......")
    GetGradesForSections(sys.argv[1], sys.argv[2])
    print('Final grades generation complete.')
    print("--------------------------------------------------------------------")
    total_students = num_students_taking_final + num_students_not_taking_final
    for grade in num_students_per_grade:
        num_students_per_grade[grade][1] = round(num_students_per_grade[grade][0] / total_students * 100,2)
    print("Students Letter grade breakdown: ", num_students_per_grade)


if __name__ == '__main__':
    main()
