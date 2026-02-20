from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from io import BytesIO


def generate_weekly_pdf(df, total_hours, senior_hours, hot_tub_hours, days_order):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Weekly Staffing Analysis Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    weekly_data = [
        ["Total Weekly Labor Hours", round(total_hours, 2)],
        ["Senior Preferred Hours", round(senior_hours, 2)],
        ["Hot Tub Hours", round(hot_tub_hours, 2)],
    ]

    weekly_table = Table(weekly_data)
    weekly_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(weekly_table)
    elements.append(Spacer(1, 20))

    for day in days_order:

        day_df = df[df["Day Name"] == day]

        if not day_df.empty:

            actual_date = day_df["Display Date"].iloc[0]

            elements.append(Paragraph(f"{day} {actual_date}", styles["Heading3"]))
            elements.append(Spacer(1, 8))

            daily_total = round(day_df["Hours"].sum(), 2)
            daily_senior = round(day_df[day_df["Senior Preferred"]]["Hours"].sum(), 2)

            summary_data = [
                ["Total Hours", daily_total],
                ["Senior Preferred Hours", daily_senior],
            ]

            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            elements.append(summary_table)
            elements.append(Spacer(1, 10))

            task_breakdown = (
                day_df.groupby("Task Type")["Hours"]
                .sum()
                .reset_index()
            )

            table_data = [["Task Type", "Hours"]]

            for _, row in task_breakdown.iterrows():
                table_data.append([row["Task Type"], round(row["Hours"], 2)])

            task_table = Table(table_data)
            task_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            elements.append(task_table)
            elements.append(Spacer(1, 20))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
