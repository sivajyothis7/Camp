# Copyright (c) 2025, siva and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class WorkerCheckin(Document):
    def validate(self):
        duplicate = frappe.db.exists(
            "Worker Checkin",
            {
                "iqama_number": self.iqama_number,
                "date": self.date
            }
        )
        if duplicate and duplicate != self.name:
            frappe.throw(
                f"A Worker Checkin already exists for Iqama {self.iqama_number} on {self.date}.",
                title="Duplicate Entry"
            )

        if self.log_type == "IN":
            last_in = frappe.get_all(
                "Worker Checkin",
                filters={
                    "iqama_number": self.iqama_number,
                    "log_type": "IN",
                    "name": ["!=", self.name],
                    "docstatus": 1
                },
                order_by="date desc",
                limit_page_length=1,
                fields=["date"]
            )
            if last_in:
                last_out = frappe.get_all(
                    "Worker Checkin",
                    filters={
                        "iqama_number": self.iqama_number,
                        "log_type": "OUT",
                        "date": [">", last_in[0].date],
                        "docstatus": 1
                    },
                    fields=["date"]
                )
                if not last_out:
                    frappe.throw(
                        f"You must check OUT after last IN on {last_in[0].date} before checking IN again.",
                        title="Missing OUT"
                    )

        if self.log_type == "Vacation Start":
            unmatched_vac_starts = frappe.get_all(
                "Worker Checkin",
                filters={
                    "iqama_number": self.iqama_number,
                    "log_type": "Vacation Start",
                    "docstatus": 1
                },
                fields=["name"]
            )
            unmatched_vac_ends = frappe.get_all(
                "Worker Checkin",
                filters={
                    "iqama_number": self.iqama_number,
                    "log_type": "Vacation End",
                    "docstatus": 1
                },
                fields=["name"]
            )
            unmatched_count = len(unmatched_vac_starts) - len(unmatched_vac_ends)
            if unmatched_count > 0:
                frappe.throw(
                    "You already have an unmatched 'Vacation Start'. Please create a 'Vacation End' first."
                )

        if self.log_type == "Vacation End":
            vac_starts = frappe.get_all(
                "Worker Checkin",
                filters={
                    "iqama_number": self.iqama_number,
                    "log_type": "Vacation Start",
                    "docstatus": 1
                },
                fields=["name"]
            )
            vac_ends = frappe.get_all(
                "Worker Checkin",
                filters={
                    "iqama_number": self.iqama_number,
                    "log_type": "Vacation End",
                    "docstatus": 1
                },
                fields=["name"]
            )
            unmatched_count = len(vac_starts) - len(vac_ends)
            if unmatched_count <= 0:
                frappe.throw("No unmatched 'Vacation Start' found. Cannot mark 'Vacation End'.")

    def on_submit(self):
        attendance_status = None

        if self.log_type == "IN":
            attendance_status = "Present"
        elif self.log_type == "OUT":
            attendance_status = "Absent"
        elif self.log_type == "Vacation Start":
            attendance_status = "Vacation"
        elif self.log_type == "Vacation End":
            last_checkin = frappe.get_all(
                "Worker Checkin",
                filters={
                    "iqama_number": self.iqama_number,
                    "date": ["<", self.date],
                    "docstatus": 1
                },
                order_by="date desc",
                limit_page_length=1,
                fields=["log_type"]
            )
            if last_checkin:
                if last_checkin[0].log_type != "OUT":
                    attendance_status = "Present"
                else:
                    attendance_status = "Absent"
            else:
                attendance_status = "Present"

        if not attendance_status:
            return

        existing_attendance = frappe.db.exists(
            "Daily Attendance",
            {
                "iqama_no": self.iqama_number,
                "date": self.date
            }
        )
        if existing_attendance:
            return

        attendance = frappe.new_doc("Daily Attendance")
        attendance.iqama_no = self.iqama_number
        attendance.worker = self.worker_name
        attendance.date = self.date
        attendance.camp_location = self.camp_location
        attendance.status = attendance_status
        attendance.reference = self.name
        attendance.insert(ignore_permissions=True)
