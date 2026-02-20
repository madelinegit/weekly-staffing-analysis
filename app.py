import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Staffing Analysis", layout="wide")

st.title("Weekly Staffing Analysis Dashboard")

st.markdown("""
### Week = Monday – Saturday

**Task Rules:**

- Regular Hot Tub Service = 30 mins  
  (Arrival Hot Tub, HO Arrival Hot Tub, Biweekly Hot Tub, Lease Hot Tub)

- Dump & Scrub = 1.5 hours  

- Post Rental Inspection = 1 hour (**Senior Preferred**)  
- Managed Services Inspection = 1 hour (**Senior Preferred**)  
- Managed Services Arrival = 1 hour (**Senior Preferred**)  
- Walk Thru = 30 mins  
- VIP = Senior Preferred  

App reads:
- Column J → Task Title  
- Column S → Due Date
""")

uploaded_file = st.file_uploader("Upload Breezeway CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # Rename columns by position
    df = df.rename(columns={
        df.columns[9]: "Task Title",
        df.columns[18]: "Due Date"
    })

    df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce")
    df = df.dropna(subset=["Due Date"])

    df = df.sort_values("Due Date")

    # Categorization logic
    def categorize_task(title):
        title = str(title).lower()

        # Regular Hot Tub (30 mins)
        if any(x in title for x in [
            "arrival hot tub",
            "ho arrival hot tub",
            "biweekly hot tub",
            "lease hot tub"
        ]):
            return "Hot Tub - Regular", 0.5, "Other"

        # Dump & Scrub
        if "dump" in title or "scrub" in title:
            return "Hot Tub - Dump & Scrub", 1.5, "Other"

        # Senior Preferred Tasks
        if "post rental inspection" in title:
            return "Post Rental Inspection", 1, "Senior Preferred"

        if "managed services inspection" in title:
            return "Managed Services Inspection", 1, "Senior Preferred"

        if "managed services arrival" in title:
            return "Managed Services Arrival", 1, "Senior Preferred"

        if "vip" in title:
            return "VIP", 1, "Senior Preferred"

        # Walk Thru
        if "walk thru" in title:
            return "Walk Thru", 0.5, "Other"

        return "Other", 0, "Other"

    df[["Task Type", "Hours", "Skill Level"]] = df["Task Title"].apply(
        lambda x: pd.Series(categorize_task(x))
    )

    # Monday–Saturday only
    df = df[df["Due Date"].dt.weekday < 6]

    # ==============================
    # WEEKLY SUMMARY
    # ==============================

    st.subheader("📊 Weekly Labor Summary (Mon–Sat)")

    total_hours = df["Hours"].sum()
    senior_hours = df[df["Skill Level"] == "Senior Preferred"]["Hours"].sum()
    hot_tub_hours = df[df["Task Type"].str.contains("Hot Tub")]["Hours"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Weekly Labor Hours", round(total_hours, 2))
    col2.metric("Senior Preferred Hours", round(senior_hours, 2))
    col3.metric("Hot Tub Hours", round(hot_tub_hours, 2))

    st.subheader("Weekly Hours by Task Type")
    weekly_summary = df.groupby("Task Type")["Hours"].sum().reset_index()
    st.dataframe(weekly_summary)

    # ==============================
    # DAILY LABOR SUMMARY
    # ==============================

    st.header("📅 Daily Labor Summary (Mon–Sat)")

    df["Day"] = df["Due Date"].dt.day_name()

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    for day in days_order:

        day_df = df[df["Day"] == day]

        if not day_df.empty:

            st.subheader(day)

            daily_total = day_df["Hours"].sum()
            daily_senior = day_df[day_df["Skill Level"] == "Senior Preferred"]["Hours"].sum()
            daily_hot_tub = day_df[day_df["Task Type"].str.contains("Hot Tub")]["Hours"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Hours", round(daily_total, 2))
            col2.metric("Senior Preferred Hours", round(daily_senior, 2))
            col3.metric("Hot Tub Hours", round(daily_hot_tub, 2))

            # Graph by Task Type
            st.markdown("#### Hours by Task Type")
            task_breakdown = day_df.groupby("Task Type")["Hours"].sum()
            st.bar_chart(task_breakdown)

            # Graph Senior vs Other
            st.markdown("#### Senior vs Other Breakdown")
            skill_breakdown = day_df.groupby("Skill Level")["Hours"].sum()
            st.bar_chart(skill_breakdown)

    st.success("Daily & Weekly Analysis Complete")
