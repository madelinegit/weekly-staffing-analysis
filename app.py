import streamlit as st
import pandas as pd
from report_generator import generate_weekly_pdf

st.set_page_config(page_title="Weekly Staffing Analysis", layout="wide")

st.title("Weekly Staffing Analysis Dashboard")

st.markdown("""
### Week = Monday – Saturday

**Senior Preferred Tasks:**
- Post Rental Inspection
- Managed Services Inspection
- Managed Services Arrival
- VIP

**Time Rules:**
- Regular Hot Tub = 0.5 hrs
- Dump & Scrub = 1.5 hrs
- Walk Thru = 0.5 hrs
- All Inspections = 1 hr
""")

uploaded_file = st.file_uploader("Upload Breezeway CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # Rename columns
    df = df.rename(columns={
        df.columns[9]: "Task Title",
        df.columns[18]: "Due Date"
    })

    df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce")
    df = df.dropna(subset=["Due Date"])
    df = df.sort_values("Due Date")

    # Categorize Tasks
    def categorize_task(title):
        title = str(title).lower()

        if any(x in title for x in [
            "arrival hot tub",
            "ho arrival hot tub",
            "biweekly hot tub",
            "lease hot tub"
        ]):
            return "Hot Tub - Regular", 0.5, False

        if "dump" in title or "scrub" or "d&s" in title:
            return "Hot Tub - Dump & Scrub", 1.5, False

        if "post rental inspection" in title:
            return "Post Rental Inspection", 1, True

        if "managed services inspection" in title:
            return "Managed Services Inspection", 1, True

        if "managed services arrival" in title:
            return "Managed Services Arrival", 1, True

        if "vip" in title:
            return "VIP", 1, True

        if "walk thru" in title:
            return "Walk Thru", 0.5, False

        return None, 0, False

    df[["Task Type", "Hours", "Senior Preferred"]] = df["Task Title"].apply(
        lambda x: pd.Series(categorize_task(x))
    )

    df = df[df["Task Type"].notnull()]
    df = df[df["Due Date"].dt.weekday < 6]

    # ==============================
    # WEEKLY SUMMARY
    # ==============================

    st.subheader("📊 Weekly Labor Summary (Mon–Sat)")

    total_hours = df["Hours"].sum()
    senior_hours = df[df["Senior Preferred"]]["Hours"].sum()
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

    df["Day Name"] = df["Due Date"].dt.day_name()
    df["Display Date"] = df["Due Date"].dt.strftime("%m/%d/%y")

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    for day in days_order:

        day_df = df[df["Day Name"] == day]

        if not day_df.empty:

            actual_date = day_df["Display Date"].iloc[0]

            st.subheader(f"{day} {actual_date}")

            daily_total = day_df["Hours"].sum()
            daily_senior = day_df[day_df["Senior Preferred"]]["Hours"].sum()
            daily_hot_tub = day_df[day_df["Task Type"].str.contains("Hot Tub")]["Hours"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Hours", round(daily_total, 2))
            col2.metric("Senior Preferred Hours", round(daily_senior, 2))
            col3.metric("Hot Tub Hours", round(daily_hot_tub, 2))

            st.markdown("#### Hours by Task Type")

            task_breakdown = (
                day_df.groupby("Task Type")["Hours"]
                .sum()
                .reset_index()
            )

            st.dataframe(task_breakdown)

    st.success("Daily & Weekly Analysis Complete")

    # ==============================
    # PDF DOWNLOAD (MUST BE INSIDE BLOCK)
    # ==============================

    st.header("📄 Download Executive Weekly Report")

    pdf = generate_weekly_pdf(
        df,
        total_hours,
        senior_hours,
        hot_tub_hours,
        days_order
    )

    st.download_button(
        label="Download Full Weekly Executive Report (PDF)",
        data=pdf,
        file_name="weekly_staffing_report.pdf",
        mime="application/pdf"
    )
