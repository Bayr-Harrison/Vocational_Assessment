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

# Function to fetch filtered data from Supabase
def fetch_filtered_data(selected_filters):
    # Connect to the database
    db_connection = get_database_connection()
    db_cursor = db_connection.cursor()

    # Build the SQL query dynamically
    query = """
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
    WHERE 1=1
    """

    # Add filters to the query
    if selected_filters["iatc_ids"]:
        query += f" AND student_list.iatc_id IN ({','.join(['%s'] * len(selected_filters['iatc_ids']))})"
    if selected_filters["exams"]:
        query += f" AND exam_results.exam IN ({','.join(['%s'] * len(selected_filters['exams']))})"
    if selected_filters["classes"]:
        query += f" AND student_list.class IN ({','.join(['%s'] * len(selected_filters['classes']))})"
    if selected_filters["curriculums"]:
        query += f" AND student_list.curriculum IN ({','.join(['%s'] * len(selected_filters['curriculums']))})"

    # Prepare parameters for the query
    params = (
        selected_filters["iatc_ids"] +
        selected_filters["exams"] +
        selected_filters["classes"] +
        selected_filters["curriculums"]
    )

    # Execute the query with the parameters
    db_cursor.execute(query, params)

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
st.title("Filter and View Exam Results")

# Sidebar filters
st.sidebar.header("Filters")

# User-selected filters
selected_filters = {
    "iatc_ids": st.sidebar.multiselect("Filter by IATC ID:", []),
    "exams": st.sidebar.multiselect("Filter by Exam:", []),
    "classes": st.sidebar.multiselect("Filter by Class:", []),
    "curriculums": st.sidebar.multiselect("Filter by Curriculum:", [])
}

# Load filter options dynamically
if st.sidebar.button("Load Filter Options"):
    db_connection = get_database_connection()
    db_cursor = db_connection.cursor()

    # Query to get unique filter options
    db_cursor.execute("SELECT DISTINCT iatc_id FROM student_list")
    selected_filters["iatc_ids"] = [row[0] for row in db_cursor.fetchall()]

    db_cursor.execute("SELECT DISTINCT exam FROM exam_results")
    selected_filters["exams"] = [row[0] for row in db_cursor.fetchall()]

    db_cursor.execute("SELECT DISTINCT class FROM student_list")
    selected_filters["classes"] = [row[0] for row in db_cursor.fetchall()]

    db_cursor.execute("SELECT DISTINCT curriculum FROM student_list")
    selected_filters["curriculums"] = [row[0] for row in db_cursor.fetchall()]

    db_cursor.close()
    db_connection.close()

    st.sidebar.success("Filter options loaded! Please select filters.")

# Load data after filters are applied
if st.sidebar.button("Apply Filters"):
    if not any(selected_filters.values()):
        st.error("Please select at least one filter to view results.")
    else:
        # Fetch filtered data
        filtered_data = fetch_filtered_data(selected_filters)

        # Display filtered data
        if not filtered_data.empty:
            st.write("Filtered Exam Results:")
            st.dataframe(filtered_data)
        else:
            st.warning("No data found for the selected filters.")
