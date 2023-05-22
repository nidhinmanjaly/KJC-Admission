import pandas as pd
import sqlite3
from admission.models import User
from django.contrib.auth.hashers import make_password, check_password

def load_student_data(excel_file_path, sqlite_file_path, table_name, interview_id):
    # Define mapping of column names from Excel to SQLite
    # column_map = {
    #     'AppNum': 'application_number',
    #     'App Status': 'application_status',
    #     'Remarks': 'application_remark',
    #     'App Date (dd/MMM/yyyy)': 'application_date',
    #     'Applicant First Name': 'first_name',
    #     'Applicant Middle Name': 'middle_name',
    #     'Applicant Last Name': 'last_name',
    #     'Date of Birth (dd/MMM/yyyy)': 'dob',
    #     'Sex': 'gender',
    #     'Nationality': 'nationality',
    #     'Student Mobile No': 'mobile_number',
    #     'Recipient': 'email_address',
    #     'Cast Category': 'cast_category',
    #     'Address line 1': 'addressline1',
    #     'Address line 2': 'addressline2',
    #     'Country': 'country',
    #     'Permanent Country': 'permanent_country',
    #     'Father Name': 'father_name',
    #     'Sub Category': 'sub_category', ## removed
    #     'Course category option': 'course_category',
    #     'UG Course Preference1': 'ug_course_preference',
    #     'AppProg': 'applied_program',
    #     'Admission Category': 'admission_category',
    #     'Law Course1': 'law_course',
    #     'Qualifying Examination': 'qualifying_exam',
    #     'Board/University': 'board_university',
    #     'Year Of Passing': 'year_of_passing',
    #     'State of Board': 'state_of_board',
    #     'Country of Board': 'country_of_board',
    #     'Other Board/University': 'other_board_or_university',
    #     'Other Qualifying Examination': 'other_qualifying_examination',
    #     'Name of the Institution': 'name_of_institution',
    #     'Aggregate Percentage (Incl. Languages)': 'aggregrate_percentage_including_language_for_UG',
    #     'Aggregate Percentage (Excl. Languages)': 'aggregrate_percentage_excluding_language_for_UG',
    #     'Aggregate Percentage': 'aggregrate_percentage_including_language_for_PG',
    #     'Aggregate Percentage Excl Languages': 'aggregrate_percentage_excluding_language_for_PG',
    #     'Tenth percentage': 'tenth_percentage',
    #     'Tenth Year': 'tenth_year',
    #     '12th percentage': 'twelfth_percentage',
    #     '12th Year': 'twelfth_year',
    #     'Result Status': 'result_status',
    #     'Qualification Detail': 'qualification_details',
    #     'District of Board': 'district_of_board',
    #     'Payment Status': 'payment_status'
    # }

    # Read Excel file into a Pandas dataframe
    df = pd.read_excel(excel_file_path)

    # convert column datatype to string
    df['App Date (dd/MMM/yyyy)'] = df['App Date (dd/MMM/yyyy)'].dt.strftime('%d/%m/%Y')
    df['Date of Birth (dd/MMM/yyyy)'] = df['Date of Birth (dd/MMM/yyyy)'].dt.strftime('%d/%m/%Y')
    df['Student Mobile No'] = df['Student Mobile No'].map(str)
    df['Year Of Passing'] = df['Year Of Passing'].fillna(0).map(int)
    df['Tenth Year'] = df['Tenth Year'].fillna(0).map(int)
    df['12th Year'] = df['12th Year'].fillna(0).map(int)
    # add interview id column
    df = df.assign(interview_id=interview_id)

    # Rename columns in dataframe using mapping
    # df = df.rename(columns=column_map)

    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_file_path)
    c = conn.cursor()

    # get list of existing application ids
    existing_applications = c.execute("SELECT application_number from admission_applicant_details").fetchall()
    existing_applications = [app[0] for app in existing_applications]

    # Insert data into SQLite table
    excel_columns = df.columns.values.tolist()
    for index, row in df.iterrows():
        app_no = str(row[excel_columns[0]])

        if app_no in existing_applications:
            interview_status = all(s is None for s in c.execute(f"SELECT interview_status_f1, interview_status_f2 from {table_name} where application_number='{app_no}'").fetchall()[0])
            # c.execute(f"SELECT interview_status_f1, interview_status_f2 from {table_name} where application_number='{app_no}'").fetchall()[0]

            if not interview_status:
                # print(app_no, interview_status)
                continue

            c.execute(f"DELETE FROM {table_name} where application_number=?",(app_no, ))
        sql = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, ?, NULL, NULL, NULL)"
        values = tuple(row[column] for column in excel_columns)
        
        c.execute(sql, values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def load_users(excel_file_path, sqlite_file_path, table_name):
    
    # Read Excel file into a Pandas dataframe
    df = pd.read_excel(excel_file_path)

    #convert password to sha256
    df['password'] = df['password'].map(make_password)
    df['user_type'] = df['user_type'].str.lower()

    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_file_path)
    c = conn.cursor()

    # get list of existing userIds
    existing_users = c.execute(f"SELECT email from {table_name}").fetchall()
    existing_users = [user[0] for user in existing_users]

    # Insert data into SQLite table
    excel_columns = df.columns.values.tolist()
    for index, row in df.iterrows():
        user_id = str(row[excel_columns[0]])

        if user_id in existing_users:
            c.execute(f"DELETE FROM {table_name} where email=?",(user_id, ))

        sql = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, False, False)"
        values = tuple(row[column] for column in excel_columns)
        # print(values)
        
        c.execute(sql, values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def load_allotment_details(excel_file_path, sqlite_file_path, table_name):
    # Read Excel file into a Pandas dataframe
    df = pd.read_excel(excel_file_path)

    # change null values to 0
    df['intake'] = df['intake'].fillna(0).map(int)
    df['admitted'] = df['admitted'].fillna(0).map(int)
    df['allotted'] = df['allotted'].fillna(0).map(int)


    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_file_path)
    c = conn.cursor()

    # get list of existing programms
    existing_progs = c.execute(f"SELECT program from {table_name}").fetchall()
    existing_progs = [prog[0] for prog in existing_progs]

    # Insert data into SQLite table
    excel_columns = df.columns.values.tolist()

    placeholders = ",".join("?" * len(excel_columns))

    for index, row in df.iterrows():

        prog = str(row[excel_columns[0]])

        if prog in existing_progs:
            c.execute(f"DELETE FROM {table_name} where program=?",(prog, ))

        sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
        values = tuple(row[column] for column in excel_columns)
        # print(values)
        
        c.execute(sql, values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def load_selection_details(excel_file_path, sqlite_file_path, table_name, interview_id):
    
    # Read Excel file into a Pandas dataframe
    df = pd.read_excel(excel_file_path)
    df = df.fillna('')

    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_file_path)
    c = conn.cursor()

    for i, row in df.iterrows():
        sql = f"UPDATE {table_name} SET selection_status='{row['selection_status']}', course_allotted='{row['course_allotted']}' WHERE application_number='{row['application_number']}';"
        print(sql)
        
        # c.execute(f"UPDATE {table_name} SET selection_status=?, course_allotted=? WHERE application_number=?;", (row['selection_status'], row['course_allotted'], row['application_number']))
        c.execute(sql)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def load_reviewers_indicators(excel_file_path, sqlite_file_path, table_name):
    # Read Excel file into a Pandas dataframe
    df = pd.read_excel(excel_file_path)
    df = df.fillna('')

    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_file_path)
    c = conn.cursor()

    # get list of existing userIds
    existing_applications = c.execute(f"SELECT application_number_id from {table_name}").fetchall()
    existing_applications = [user[0] for user in existing_applications]

    # Insert data into SQLite table
    excel_columns = df.columns.values.tolist()
    for index, row in df.iterrows():
        appno = str(row[excel_columns[0]])

        if appno in existing_applications:
            c.execute(f"DELETE FROM {table_name} where application_number_id=?",(appno, ))

        sql = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)"
        values = tuple(row[column] for column in excel_columns)
        
        c.execute(sql, values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Must import the script as a module to call it")