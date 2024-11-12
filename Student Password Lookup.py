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

# Function to fetch data from the 'student_list' table in Supabase
def fetch_data_from_supabase():
    # Connect to the database
    db_connection = get_database_connection()
    db_cursor = db_connection.cursor()

    # SQL query to select all active students
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
st.title("View and Filter Student Data")

# Fetch data from Supabase
data = fetch_data_from_supabase()

# Sidebar filters for Student ID
st.sidebar.header("Filter by IATC ID")
iatc_id_options = data['IATC ID'].unique()
selected_iatc_ids = st.sidebar.multiselect("Select IATC ID(s):", iatc_id_options, default=iatc_id_options)

# Apply filters to the data
filtered_data = data[data['IATC ID'].isin(selected_iatc_ids)]

# Display the filtered data in a table format
st.write("Filtered Student Data:")
st.dataframe(filtered_data)  # Interactive table
