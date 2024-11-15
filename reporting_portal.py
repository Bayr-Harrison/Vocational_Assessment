import os
import pg8000
import pandas as pd
import streamlit as st

# Set a simple password
PASSWORD = os.environ["APP_PASSWORD"]

# Password input for access
password = st.text_input("Enter Password", type="password")
if password != PASSWORD:
    st.warning("Incorrect password")
    st.stop()
else:
    st.success("Access granted!")

# Function to establish a database connection
def get_database_connection():
    db_connection = pg8000.connect(
        database=os.environ["SUPABASE_DB_NAME"],
        user=os.environ["SUPABASE_USER"],
        password=os.environ["SUPABASE_PASSWORD"],
        host=os.environ["SUPABASE_HOST"],
        port=os.environ["SUPABASE_PORT"]
    )
    return db_connection

# Function to fetch exam results from the Supabase database
def fetch_exam_results():
    # Connect to the database
    db_connection = get_database_connection()
    db_cursor = db_connection.cursor()

    # SQL query to fetch active exam results
    db_query = """
    SELECT
        student_list.iatc_id,
        exam_results.nat_id,
        student_list.name,
        student_list.curriculum,
        student_list.class,
        exam_results.exam,
        exam_results.score,
        exam_results.result,
        exam_results.date,
        exam_results.session,
        exam_results.type,
        exam_results.attempt_index,
        exam_results.score_index

    FROM
        exam_results
    
    INNER JOIN
        student_list ON exam_results.nat_id = student_list.nat_id
    ;
    """
    db_cursor.execute(db_query)

    # Fetch data and convert it to a DataFrame
    rows = db_cursor.fetchall()
    column_names = [
        'IATC ID',
        'National ID',
        'Name',
        'Curriculum',
        'Class',
        'Exam',
        'Score',
        'Result',
        'Date',
        'Session Time',
        'Exam Type',
        'Attempt No.',
        'Score Index'
    ]
    data = pd.DataFrame(rows, columns=column_names)

    # Close the connection
    db_cursor.close()
    db_connection.close()

    return data

# Streamlit interface
st.title("View and Filter Exam Results")

# Fetch exam results from Supabase
exam_data = fetch_exam_results()

# Default filtering
default_iatc_id = exam_data['IATC ID'].iloc[0] if not exam_data.empty else None
default_exam = exam_data['Exam'].iloc[0] if not exam_data.empty else None

# Sidebar filters
st.sidebar.header("Filters")

# Filter by IATC ID
iatc_id_options = exam_data['IATC ID'].unique()
selected_iatc_id = st.sidebar.multiselect("Filter by IATC ID:", iatc_id_options, default=[default_iatc_id])

# Filter by Exam
exam_options = exam_data['Exam'].unique()
selected_exam = st.sidebar.multiselect("Filter by Exam:", exam_options, default=[default_exam])

# Apply default filters to the data
filtered_data = exam_data[
    (exam_data['IATC ID'].isin(selected_iatc_id)) & 
    (exam_data['Exam'].isin(selected_exam))
]

# Display filtered data
st.write(f"Filtered Exam Results for Selected IATC IDs and Exams")
st.dataframe(filtered_data)  # Interactive table
