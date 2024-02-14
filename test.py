import streamlit as st
import mysql.connector
from mysql.connector import Error
import random
import hashlib

# Function to create SQL connection
def create_database_connection(host, database, username, password):
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=username,
            password=password  
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            st.success(f"Connected to MySQL Server version {db_info}")
            return connection
    except Error as e:
        st.error(f"Error while connecting to MySQL: {e}")
        return None

# Function to fetch tables and create dropdown
def select_table(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    selected_table = st.selectbox("Select a table:", table_names)
    st.success(f"You selected table: {selected_table}")
    return selected_table

# Function to display columns of selected table
def display_columns(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"DESCRIBE {table_name};")
    columns = cursor.fetchall()
    column_names = [column[0] for column in columns]
    st.success(f"Columns of {table_name}: {', '.join(column_names)}")
    return column_names

# Function to fetch data from selected columns
def fetch_column_data(connection, table_name, selected_columns):
    cursor = connection.cursor()
    selected_columns_str = ', '.join(selected_columns)
    cursor.execute(f"SELECT {selected_columns_str} FROM {table_name};")
    data = cursor.fetchall()
    return data

# Function to fetch MySQL users
def fetch_mysql_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM mysql.user;")
    users = cursor.fetchall()
    user_list = [user[0] for user in users]
    return user_list

# Function to perform data anonymization
def anonymize_data(data, anonymization_mode):
    anonymized_data = []
    for row in data:
        anonymized_row = []
        for value in row:
            if anonymization_mode == "None":
                anonymized_row.append(value)
            elif anonymization_mode == "Pseudonymization":
                anonymized_row.append(f"User_{random.randint(1000, 9999)}")
            elif anonymization_mode == "Generalization":
                anonymized_row.append("Sensitive")
            elif anonymization_mode == "Randomization":
                anonymized_row.append(random.randint(0, 100))
            elif anonymization_mode == "Data Masking":
                anonymized_row.append("XXXXX")
            elif anonymization_mode == "Hashing":
                anonymized_row.append(hashlib.sha256(str(value).encode()).hexdigest())
            else:
                anonymized_row.append(value)
        anonymized_data.append(anonymized_row)
    return anonymized_data

# Function to display selected column data with anonymization
def display_selected_column_data(connection, table_name, selected_columns, selected_user, anonymization_mode):
    column_data = fetch_column_data(connection, table_name, selected_columns)
    st.write("Original Data:")
    st.write(column_data)
    st.write("Anonymized Data:")
    anonymized_data = anonymize_data(column_data, anonymization_mode)
    st.write(anonymized_data)

# Streamlit app
def main():
    st.title("MySQL Database Connection ")

    # Input fields for host, database, username, and password
    host = st.text_input("Enter MySQL Host:")
    database = st.text_input("Enter Database Name:")
    username = st.text_input("Enter Username:")
    password = st.text_input("Enter Password:", type="password")

    # Button to initiate database connection
    st.button("Connect to MySQL Database")
    
    if host and database and username and password:
        connection = create_database_connection(host, database, username, password)
        if connection:
            selected_table = select_table(connection)
            column_names = display_columns(connection, selected_table)
            selected_columns = st.multiselect("Select columns to anonymize:", column_names)

            # Fetch MySQL users
            mysql_users = fetch_mysql_users(connection)
            selected_user = st.selectbox("Select MySQL User:", mysql_users)

            if selected_columns and selected_user:
                anonymization_modes = ["None", "Pseudonymization", "Generalization", "Randomization", "Data Masking", "Hashing"]
                selected_anonymization_mode = st.selectbox("Select Anonymization Mode:", anonymization_modes)
                display_selected_column_data(connection, selected_table, selected_columns, selected_user, selected_anonymization_mode)

if __name__ == "__main__":
    main()
