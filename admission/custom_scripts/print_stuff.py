
import pandas as pd
import sqlite3

# db_path = "../../db.sqlite3"

def get_remarks(db_file_path, out_file="remarks_sheet.xlsx"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file_path)
    # Fetch the table data using a SELECT statement
    # data = pd.read_sql_query("SELECT * FROM admission_user", conn)
    data = pd.read_sql_query("SELECT * FROM admission_remarks", conn)
    # Write the data to an Excel file
    writer = pd.ExcelWriter(out_file, engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()

    conn.close()
    return out_file

# get_remarks(db_path)