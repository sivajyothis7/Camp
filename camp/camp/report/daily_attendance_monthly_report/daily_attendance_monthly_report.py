# Copyright (c) 2025, siva and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Iqama ID"),
            "fieldname": "iqama_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Worker Name"),
            "fieldname": "worker",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("First Present Date"),
            "fieldname": "first_present_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": _("Last Present Date"),
            "fieldname": "last_present_date",
            "fieldtype": "Date",
            "width": 150
        }
    ]
    
    # Add day columns (1-31)
    for day in range(1, 32):
        columns.append({
            "label": str(day),
            "fieldname": str(day),
            "fieldtype": "HTML",
            "width": 45
        })
    
    return columns

def get_data(filters):
    month_num = get_month_number(filters.get("month"))
    year = filters.get("year")
    
    data = frappe.db.sql(f"""
        WITH month_info AS (
            SELECT {month_num} AS month_num
        )
        
        SELECT 
            da.iqama_no,
            da.worker,
            
            MIN(CASE 
                WHEN da.status = 'Present' AND MONTH(da.date) = (SELECT month_num FROM month_info) AND YEAR(da.date) = %(year)s 
                THEN da.date 
                END) AS first_present_date,
            
            MAX(CASE 
                WHEN da.status = 'Present' AND MONTH(da.date) = (SELECT month_num FROM month_info) AND YEAR(da.date) = %(year)s 
                THEN da.date 
                END) AS last_present_date,
    """ + get_day_columns_sql() + """
        FROM 
            `tabDaily Attendance` da
        WHERE
            da.docstatus = 0
            AND MONTH(da.date) = (SELECT month_num FROM month_info)
            AND YEAR(da.date) = %(year)s
        GROUP BY 
            da.iqama_no, da.worker
        ORDER BY 
            da.worker
    """, {"year": year}, as_dict=1)
    
    return data

def get_day_columns_sql():
    day_columns = []
    for day in range(1, 32):
        day_columns.append(f"""
            MAX(CASE 
                WHEN DAY(da.date) = {day} 
                     AND MONTH(da.date) = (SELECT month_num FROM month_info) 
                     AND YEAR(da.date) = %(year)s THEN
                    CASE 
                        WHEN da.status = 'Present' THEN '<span style="color:green;">P</span>'
                        WHEN da.status = 'Vacation' THEN '<span style="color:orange;">V</span>'
                        ELSE '<span style="color:red;">CO</span>'
                    END
                ELSE '<span style="color:#DC143C;">CO</span>'
            END) AS `{day}`
        """)
    return ",".join(day_columns)

def get_month_number(month_name):
    months = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    return months.get(month_name, 0)