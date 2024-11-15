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

# Dynamically create filters for each column
filtered_data = exam_data.copy()
for column in exam_data.columns:
    options = exam_data[column].dropna().unique()
    if column == 'IATC ID':
        selected_option = st.sidebar.multiselect(f"Filter by {column}:", options, default=[default_iatc_id])
    elif column == 'Exam':
        selected_option = st.sidebar.multiselect(f"Filter by {column}:", options, default=[default_exam])
    else:
        selected_option = st.sidebar.multiselect(f"Filter by {column}:", options, default=options)

    # Apply the filter
    if selected_option:
        filtered_data = filtered_data[filtered_data[column].isin(selected_option)]

# Display filtered data
st.write("Filtered Exam Results:")
st.dataframe(filtered_data)  # Interactive table
