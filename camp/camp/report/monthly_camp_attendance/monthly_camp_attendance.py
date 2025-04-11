# Copyright (c) 2025, siva and contributors
# For license information, please see license.txt

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
        "name", "worker_name", "iqama_number", "category", "job_title", "nationality", "per_day_food_rate", "per_day_rent"
    ])

    data = []

    for worker in workers:
        row = {
            "name": worker.worker_name,
            "iqama": worker.iqama_number,
            "category": worker.category,
            "job_title": worker.job_title,
            "nationality": worker.nationality,
        }

        present = vacation = absent = 0

        for day in day_range:
            date_str = f"{year}-{month:02d}-{day:02d}"
            status = frappe.db.get_value("Daily Attendance", {
                "worker": worker.name,
                "date": date_str
            }, "status")

            mark = ""
            if status == "Present":
                mark = "Y"
                present += 1
            elif status == "Absent":
                mark = "V"
                vacation += 1
            else:
                mark = "A"
                absent += 1

            row[f"day_{day}"] = mark

        row["present"] = present
        row["vacation"] = vacation
        row["absent"] = absent
        row["amount"] = round((worker.per_day_food_rate or 0) + (worker.per_day_rent or 0)) * present

        data.append(row)

    return columns, data
