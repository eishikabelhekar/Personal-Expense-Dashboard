import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("💰 Personal Finance Dashboard")

DATA_FILE = "transactions.csv"

# Load data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)

    # Ensure Date column is proper datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
else:
    df = pd.DataFrame(
        columns=['Date', 'Type', 'Category', 'Amount', 'Description']
    )
    df.to_csv(DATA_FILE, index=False)

# Sidebar - Add Transaction
st.sidebar.header("Add New Transaction")

with st.sidebar.form("transaction_form"):
    date = st.date_input("Date", datetime.today())

    trans_type = st.selectbox(
        "Type",
        ["Income", "Expense"]
    )

    categories = (
        ["Salary", "Freelance", "Investment", "Other"]
        if trans_type == "Income"
        else [
            "Food",
            "Transport",
            "Rent",
            "Utilities",
            "Entertainment",
            "Shopping",
            "Health",
            "Other"
        ]
    )

    category = st.selectbox("Category", categories)

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=0.01
    )

    description = st.text_input("Description")

    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        new_row = pd.DataFrame([{
            "Date": pd.Timestamp(date),
            "Type": trans_type,
            "Category": category,
            "Amount": amount,
            "Description": description
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("✅ Transaction added!")
        st.rerun()

# Dashboard
if not df.empty:

    # Ensure Date column remains datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    # Convert filter dates to Timestamp
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    filtered_df = df[
        (df['Date'] >= start_ts) &
        (df['Date'] <= end_ts)
    ].copy()

    # Metrics
    total_income = filtered_df.loc[
        filtered_df['Type'] == 'Income',
        'Amount'
    ].sum()

    total_expense = filtered_df.loc[
        filtered_df['Type'] == 'Expense',
        'Amount'
    ].sum()

    balance = total_income - total_expense

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Income", f"₹{total_income:,.2f}")
    c2.metric("Total Expenses", f"₹{total_expense:,.2f}")
    c3.metric("Net Balance", f"₹{balance:,.2f}")
    c4.metric("Transactions", len(filtered_df))

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "Spending by Category",
        "Monthly Trend",
        "All Transactions"
    ])

    # Expense Pie Chart
    with tab1:
        expense_df = filtered_df[
            filtered_df['Type'] == 'Expense'
        ]

        if not expense_df.empty:
            fig = px.pie(
                expense_df,
                names='Category',
                values='Amount',
                title="Expense Breakdown"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("No expense data available.")

    # Monthly Trend
    with tab2:
        if not filtered_df.empty:

            trend_df = filtered_df.copy()

            trend_df['Month'] = (
                trend_df['Date']
                .dt.to_period('M')
                .astype(str)
            )

            monthly = (
                trend_df
                .groupby(['Month', 'Type'])['Amount']
                .sum()
                .unstack(fill_value=0)
                .reset_index()
            )

            fig = px.line(
                monthly,
                x='Month',
                y=monthly.columns[1:],
                markers=True,
                title="Income vs Expenses Trend"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("No data available.")

    # Transactions Table
    with tab3:
        st.dataframe(
            filtered_df.sort_values(
                'Date',
                ascending=False
            ),
            use_container_width=True
        )

        csv = filtered_df.to_csv(
            index=False
        ).encode('utf-8')

        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv"
        )

else:
    st.info(
        "Add transactions using the sidebar to see your dashboard come alive!"
    )

st.caption(
    "Personal Finance Dashboard • Built with ❤️ using Python & Streamlit"
)