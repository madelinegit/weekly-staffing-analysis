import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Weekly Staffing Analysis", layout="wide")

st.title("Weekly Staffing Analysis Dashboard")

st.markdown("""
Upload a Breezeway CSV export.
- Column J = Task Title
- Column S = Due Date
App will:
• Sort by date
• Categorize task types
• Calculate total labor hours
""")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # Rename based on position (Column J = index 9, Column S = index 18)
    df = df.rename(columns={
        df.columns[9]: "Task Title",
        df.columns[18]: "Due Date"
    })

    df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce")
    df = df.dropna(subset=["Due Date"])

    # Sort by date
    df = df.sort_values("Due Date")

    # Define time logic
    def categorize_task(title):
        title = str(title).lower()

        # Hot tub regular (30 mins)
        if any(x in title for x in [
            "arrival hot tub",
            "ho arrival hot tub",
            "biweekly hot tub",
            "lease hot tub"
        ]):
            return "Hot Tub - Regular", 0.5, "Other"

        # Dump & Scrub (1.5 hrs)
        if "dump" in title or "scrub" in title:
            return "Hot Tub - Dump & Scrub", 1.5, "Other"

        # Post Rental Inspection (1 hr)
        if "post rental inspection" in title:
            return "Post Rental Inspection", 1, "Senior Preferred"

        # Managed Services Arrival (1 hr)
        if "managed services arrival" in title:
            return "Managed Services Arrival", 1, "Senior Preferred"

        # Walk Thru (30 mins)
        if "walk thru" in title:
            return "Walk Thru", 0.5, "Other"

        # Managed Services Inspection (1 hr)
        if "managed services inspection" in title:
            return "Managed Services Inspection", 1, "Senior Preferred"

        # VIP (assume 1 hr)
        if "vip" in title:
            return "VIP", 1, "Senior Preferred"

        return "Other", 0, "Other"

    df[["Task Type", "Hours", "Skill Level"]] = df["Task Title"].apply(
        lambda x: pd.Series(categorize_task(x))
    )

    # Filter Monday–Saturday
    df = df[df["Due Date"].dt.weekday < 6]

    total_hours = df["Hours"].sum()

    summary = df.groupby("Task Type")["Hours"].sum().reset_index()
    senior_hours = df[df["Skill Level"] == "Senior Preferred"]["Hours"].sum()

    st.subheader("📊 Weekly Labor Summary (Mon–Sat)")
    st.metric("Total Labor Hours", round(total_hours, 2))
    st.metric("Senior-Preferred Hours", round(senior_hours, 2))

    st.subheader("Hours by Task Type")
    st.dataframe(summary)

    st.subheader("Task Breakdown by Date")
    date_summary = df.groupby(df["Due Date"].dt.date)["Hours"].sum()
    st.bar_chart(date_summary)

    st.success("Analysis Complete")
