import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import pytz

# Function to establish the MySQL (TiDB) connection
def init_connection():
    return mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",  # TiDB Cloud host
        port=4000,  # TiDB Cloud port
        user="nVBqARTHPX1yFUJ.root",  # Your TiDB Cloud username
        password="L9Rs0LXsGYRYZyIE",  # Your TiDB Cloud password
        database="fortune500",  # Your TiDB Cloud database name
        ssl_ca="ca-cert.pem"  # Path to the SSL certificate
    )

def add_transaction(user_id, date_time, category, description, amount, transaction_type, payment_method):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        INSERT INTO transactions (user_id, date_time, category, description, amount, transaction_type, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, date_time, category, description, amount, transaction_type, payment_method))
    conn.commit()
    conn.close()

def fetch_transactions(user_id):
    conn = init_connection()
    transactions_df = pd.read_sql_query(f"SELECT * FROM transactions WHERE user_id = {user_id}", conn)
    conn.close()
    return transactions_df

# Login form
def login():
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = authenticate_user(email, password)
        if user_id:
            st.session_state.user_id = user_id
            st.success("Logged in successfully")
        else:
            st.error("Invalid credentials")

def authenticate_user(email, password):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s AND password = %s", (email, password))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

# Check if user is logged in
if 'user_id' in st.session_state:
    user_id = st.session_state.user_id
    st.title("Monthly Expenditure Tracker")
    # Add form for transactions here

    # Add new transaction logic (with user_id)
    date = st.date_input("Date")
    time = st.text_input("Time", datetime.now().strftime('%H:%M:%S'))
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Salary", "Investment", "Others"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    transaction_type = st.selectbox("Transaction Type", ["Cash In", "Cash Out"])
    payment_method = st.radio("Payment Method", ["Cash", "Online"])

    if st.button("Add Transaction"):
        date_time = f"{date} {time}"
        add_transaction(user_id, date_time, category, description, amount, transaction_type, payment_method)

    # Display user's transactions
    transactions_df = fetch_transactions(user_id)
    st.dataframe(transactions_df)
else:
    login()  # Show login form if not logged in
