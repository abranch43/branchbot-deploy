"""Streamlit live dashboard for BranchOS revenue tracking."""
import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="BranchOS Income Ingest",
    page_icon="💰",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("BranchOS Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Income Ingest", "Revenue Summary", "Transaction History"]
)

# Helper functions
def get_revenue_summary():
    """Fetch revenue summary from API."""
    try:
        response = requests.get(f"{API_URL}/revenue/summary")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching summary: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def get_revenue_events(limit=50):
    """Fetch recent revenue events from API."""
    try:
        response = requests.get(f"{API_URL}/revenue/events?limit={limit}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching events: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []


def submit_manual_transaction(amount, currency, email, customer_id, entity, description):
    """Submit a manual transaction to API."""
    try:
        data = {
            "amount": amount,
            "currency": currency,
            "customer_email": email if email else None,
            "customer_id": customer_id if customer_id else None,
            "entity": entity if entity else None,
            "description": description if description else None
        }
        response = requests.post(f"{API_URL}/ingest/manual", json=data)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error connecting to API: {str(e)}"


def upload_csv(file, amount_col, currency_col, email_col, entity_col, description_col):
    """Upload CSV file to API."""
    try:
        files = {"file": file}
        data = {
            "amount_column": amount_col,
            "currency_column": currency_col if currency_col else "",
            "email_column": email_col if email_col else "",
            "entity_column": entity_col if entity_col else "",
            "description_column": description_col if description_col else ""
        }
        response = requests.post(f"{API_URL}/ingest/csv", files=files, data=data)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error connecting to API: {str(e)}"


# Main content based on selected page
if page == "Income Ingest":
    st.title("💰 Universal Income Ingest")
    st.markdown("Track all revenue streams in one place - manual entries, CSV imports, and automated webhooks.")
    
    # Display summary metrics at top
    summary = get_revenue_summary()
    if summary:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Revenue",
                f"${summary['total_dollars']:,.2f}",
                delta=None
            )
        with col2:
            st.metric(
                "Transaction Count",
                f"{summary['count']:,}",
                delta=None
            )
    
    st.markdown("---")
    
    # Two column layout for manual entry and CSV upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Manual Transaction Entry")
        with st.form("manual_entry"):
            amount = st.number_input("Amount ($)", min_value=0.01, value=100.00, step=0.01)
            currency = st.text_input("Currency", value="USD")
            email = st.text_input("Customer Email (optional)")
            customer_id = st.text_input("Customer ID (optional)")
            entity = st.selectbox(
                "Business Entity (optional)",
                ["", "A+ Enterprise LLC", "Legacy Unchained Inc"]
            )
            description = st.text_area("Description (optional)")
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted:
                result, error = submit_manual_transaction(
                    amount, currency, email, customer_id, entity, description
                )
                if result:
                    st.success(f"✅ Transaction added successfully! ID: {result['event_id']}")
                    st.rerun()
                else:
                    st.error(error)
    
    with col2:
        st.subheader("📊 CSV Upload")
        st.markdown("Upload a CSV file with revenue transactions. Map your columns below.")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file:
            # Preview CSV
            df = pd.read_csv(uploaded_file)
            st.write("**Preview:**")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Column mapping
            st.write("**Column Mapping:**")
            columns = list(df.columns)
            
            amount_col = st.selectbox("Amount Column *", columns, key="amount_col")
            currency_col = st.selectbox("Currency Column (optional)", [""] + columns, key="currency_col")
            email_col = st.selectbox("Email Column (optional)", [""] + columns, key="email_col")
            entity_col = st.selectbox("Entity Column (optional)", [""] + columns, key="entity_col")
            description_col = st.selectbox("Description Column (optional)", [""] + columns, key="desc_col")
            
            if st.button("Upload & Process CSV"):
                # Reset file pointer again before upload
                uploaded_file.seek(0)
                result, error = upload_csv(
                    uploaded_file,
                    amount_col,
                    currency_col if currency_col else None,
                    email_col if email_col else None,
                    entity_col if entity_col else None,
                    description_col if description_col else None
                )
                
                if result:
                    st.success(f"✅ CSV processed! Created {result['created_count']} transactions out of {result['total_rows']} rows.")
                    if result.get('errors'):
                        st.warning(f"⚠️ Errors: {', '.join(result['errors'][:5])}")
                    st.rerun()
                else:
                    st.error(error)

elif page == "Revenue Summary":
    st.title("📊 Revenue Summary")
    
    summary = get_revenue_summary()
    if summary:
        # Big metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${summary['total_dollars']:,.2f}",
                help="All-time total revenue"
            )
        
        with col2:
            st.metric(
                "Transaction Count",
                f"{summary['count']:,}",
                help="Total number of transactions"
            )
        
        with col3:
            avg = summary['total_dollars'] / summary['count'] if summary['count'] > 0 else 0
            st.metric(
                "Average Transaction",
                f"${avg:,.2f}",
                help="Average transaction value"
            )

elif page == "Transaction History":
    st.title("📜 Transaction History")
    
    # Filters
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("View recent revenue transactions")
    with col2:
        limit = st.selectbox("Show", [25, 50, 100, 250], index=1)
    
    # Fetch and display events
    events = get_revenue_events(limit=limit)
    
    if events:
        # Convert to DataFrame for better display
        df_data = []
        for event in events:
            df_data.append({
                "Date": datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'),
                "Amount": f"${event['amount_dollars']:,.2f}",
                "Provider": event['provider'],
                "Type": event['event_type'],
                "Email": event.get('customer_email', 'N/A'),
                "Entity": event.get('entity', 'N/A'),
                "Event ID": event['event_id']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown(f"**Total transactions shown:** {len(events)}")
    else:
        st.info("No transactions found. Add some transactions using the Income Ingest page!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**BranchOS** Revenue Tracking System")
st.sidebar.markdown("Maintainer: Antonio Branch")

