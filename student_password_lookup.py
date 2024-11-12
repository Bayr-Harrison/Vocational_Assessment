import os
import pg8000
import pandas as pd
import streamlit as st

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

# Function to fetch data from the 'exam_results' table in Supabase
def fetch_data_from_supabase():
    # Connect to the database
    db_connection = get_database_connection()
    db_cursor = db_connection.cursor()

    # SQL query to select all data from the 'exam_results' table
    db_query = "SELECT iatc_id, name, class, password FROM student_list WHERE status = 'ACTIVE';"
    db_cursor.execute(db_query)

    # Fetch all rows and convert to a DataFrame
    rows = db_cursor.fetchall()
    column_names = ['IATC ID', 'Name', 'Class', 'Password'] 
    data = pd.DataFrame(rows, columns=column_names)

    # Close the connection
    db_cursor.close()
    db_connection.close()

    return data

# Streamlit interface for displaying data
st.title("View and Filter Data")

# Fetch data from Supabase
data = fetch_data_from_supabase()

# Set default selection to the first student's IATC ID on initial load
first_student_id = data['IATC ID'].iloc[0] if not data.empty else None

# Sidebar filters
st.sidebar.header("Select Student ID")

# Filter by 'IATC ID'
exam_options = data['IATC ID'].unique()
selected_exam = st.sidebar.multiselect("Select Student(s):", exam_options, default=[first_student_id])

# Apply filters to the data
filtered_data = data[data['IATC ID'].isin(selected_exam)]

# Display the filtered data in a table format
st.write("Filtered Student Data:")
st.dataframe(filtered_data)  # Interactive table
