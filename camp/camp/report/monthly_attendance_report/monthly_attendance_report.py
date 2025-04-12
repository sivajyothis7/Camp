import frappe
import calendar
from datetime import datetime

def execute(filters=None):
    if not filters:
        return [], []

    month = int(filters.get("month"))
    year = int(filters.get("year"))

    _, days_in_month = calendar.monthrange(year, month)
    day_range = [day for day in range(1, days_in_month + 1)]

    columns = [
        {"label": "Iqama", "fieldname": "iqama", "fieldtype": "Data"},
        {"label": "Name", "fieldname": "name", "fieldtype": "Data"},
        {"label": "Category", "fieldname": "category", "fieldtype": "Data"},
        {"label": "Job Title", "fieldname": "job_title", "fieldtype": "Data"},
        {"label": "Nationality", "fieldname": "nationality", "fieldtype": "Data"},
        {"label": "Company", "fieldname": "company", "fieldtype": "Data"},  
        {"label": "Check In", "fieldname": "check_in", "fieldtype": "Data"},
        {"label": "Check Out", "fieldname": "check_out", "fieldtype": "Data"},


    ]

    for day in day_range:
        columns.append({
            "label": str(day),
            "fieldname": f"day_{day}",
            "fieldtype": "Data",
            "width": 30
        })

    columns += [
        {"label": "Present", "fieldname": "present", "fieldtype": "Int"},
        {"label": "Vacation", "fieldname": "vacation", "fieldtype": "Int"},
        {"label": "Absent", "fieldname": "absent", "fieldtype": "Int"},
        {"label": "Amount (₹)", "fieldname": "amount", "fieldtype": "Currency"},
    ]

    workers = frappe.get_all("Worker Profile", fields=[
        "name", "worker_name", "iqama_number", "category",
        "job_title", "nationality", "company", "per_day_food_rate", "per_day_rent"
    ])

    data = []

    for worker in workers:
        row = {
            "name": worker.worker_name,
            "iqama": worker.iqama_number,
            "category": worker.category,
            "job_title": worker.job_title,
            "nationality": worker.nationality,
            "company": worker.company,  
        }

        present = vacation = absent = 0
        check_in_time = check_out_time = ""

        for day in day_range:
            date_str = f"{year}-{month:02d}-{day:02d}"
            status = frappe.db.get_value("Daily Attendance", {
                "worker": worker.name,
                "date": date_str
            }, "status")

            check_in = frappe.db.get_value("Daily Attendance", {
                "worker": worker.name,
                "date": date_str
            }, "check_in_date")

            check_out = frappe.db.get_value("Daily Attendance", {
                "worker": worker.name,
                "date": date_str
            }, "check_out_date")

            mark = ""
            if status == "Present":
                mark = "P"
                present += 1
            elif status == "Vacation":
                mark = "V"
                vacation += 1
            else:
                mark = "O"
                absent += 1

            row[f"day_{day}"] = mark

            row["check_in"] = check_in if check_in else ""
            row["check_out"] = check_out if check_out else ""

        row["present"] = present
        row["vacation"] = vacation
        row["absent"] = absent

        rate = (worker.per_day_food_rate or 0) + (worker.per_day_rent or 0)
        row["amount"] = round(rate * present)

        data.append(row)

    return columns, data
