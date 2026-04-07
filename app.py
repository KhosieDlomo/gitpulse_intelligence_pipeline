import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import GitPulseDB

# Page Configuration
st.set_page_config(page_title="GitPulse Intelligence", page_icon="🚀", layout="wide")

# Initialize Database Connection
db = GitPulseDB("data/gitpulse.db")

def load_data():
    query = "SELECT repo_name, stars, label, summary, captured_at FROM repo_history ORDER BY captured_at DESC"
    df = pd.read_sql(query, db.conn)
    return df

# --- UI HEADER ---
st.title("🚀 GitPulse: Open Source Intelligence")
st.markdown("Automated tracking of trending **Python, Java, and C++** repositories.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Intelligence Filters")
data = load_data()

if not data.empty:
    # Filter by Category 
    categories = ["All"] + list(data['label'].unique())
    selected_cat = st.sidebar.selectbox("Select Project Category", categories)

    # Filter Logic
    filtered_df = data if selected_cat == "All" else data[data['label'] == selected_cat]

    # --- MAIN DASHBOARD ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Latest Discoveries: {selected_cat}")
        for _, row in filtered_df.head(10).iterrows():
            with st.expander(f"⭐ {row['stars']} | {row['repo_name']}"):
                st.write(f"**Category:** `{row['label']}`")
                st.write(f"**AI Summary:** {row['summary']}")
                st.caption(f"Captured on: {row['captured_at']}")

    with col2:
        st.subheader("Language Distribution")
        # Creating a quick visual for categories
        fig = px.pie(filtered_df, names='label', hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data found in gitpulse.db yet. Run main.py to fetch some repos!")

# --- FOOTER ---
st.divider()
st.caption("GitPulse Intelligence Pipeline | Built for Scale & Resilience")