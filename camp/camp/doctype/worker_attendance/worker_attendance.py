from datetime import timedelta, datetime
import frappe
from frappe.model.document import Document


class WorkerAttendance(Document):
    def validate(self):
        def get_month_year(d):
            return d.month, d.year

        def safe_date(d):
            return datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d

        if not self.check_in_date:
            frappe.throw("Check-in Date is required.")

        check_in_date = safe_date(self.check_in_date)
        month = check_in_date.month
        year = check_in_date.year

        existing = frappe.db.exists(
            "Worker Attendance",
            {
                "worker": self.worker,
                "docstatus": ["<", 2],
                "name": ["!=", self.name],
                "check_in_date": ["between", [f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"]],
            }
        )

        if existing:
            frappe.throw(f"Worker '{self.worker}' already has an attendance record for {check_in_date.strftime('%B %Y')}.")

        if self.enable_check_in and self.enable_check_out and self.check_out_date:
            out_date = safe_date(self.check_out_date)
            if get_month_year(check_in_date) != get_month_year(out_date):
                frappe.throw("Check-in and Check-out dates must be within the same month.")

        if self.vacation_out_date and self.vacation_in_date:
            vac_out = safe_date(self.vacation_out_date)
            vac_in = safe_date(self.vacation_in_date)

            if get_month_year(vac_out) != get_month_year(vac_in):
                frappe.throw("Vacation Out and In dates must be within the same month.")


def auto_mark_attendance(doc, method):
    if not doc.enable_check_in or not doc.check_in_date:
        return

    def safe_date(d):
        return datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d

    today = datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d").date()

    check_in_date = safe_date(doc.check_in_date)
    check_out_date = safe_date(doc.check_out_date) if doc.check_out_date else None
    vacation_out_date = safe_date(doc.vacation_out_date) if doc.vacation_out_date else None
    vacation_in_date = safe_date(doc.vacation_in_date) if doc.vacation_in_date else None

    start_date = check_in_date

    if doc.enable_check_out and check_out_date:
        end_date = check_out_date
    elif vacation_out_date:
        end_date = vacation_out_date - timedelta(days=1)
    else:
        end_date = today

    delete_existing_entries(doc.worker, start_date, end_date)
    create_attendance_entries(doc.worker, start_date, end_date, status="Present", source_doc=doc)

    if vacation_out_date and vacation_in_date:
        vacation_start = vacation_out_date
        vacation_end = vacation_in_date - timedelta(days=1)
        delete_existing_entries(doc.worker, vacation_start, vacation_end)
        create_attendance_entries(doc.worker, vacation_start, vacation_end, status="Vacation", source_doc=doc)

    if vacation_in_date:
        resume_start = vacation_in_date
        resume_end = check_out_date if doc.enable_check_out and check_out_date else today
        delete_existing_entries(doc.worker, resume_start, resume_end)
        create_attendance_entries(doc.worker, resume_start, resume_end, status="Present", source_doc=doc)

    mark_absents_for_month(doc.worker, check_in_date, doc)


def create_attendance_entries(worker, start_date, end_date, status="Present", source_doc=None):
    current = start_date
    while current <= end_date:
        doc = frappe.get_doc({
            "doctype": "Daily Attendance",
            "worker": worker,
            "date": current,
            "status": status,
            "worker_attendance": source_doc.name if source_doc else None,
            "check_in_date": source_doc.check_in_date if source_doc else None,
            "check_out_date": source_doc.check_out_date if source_doc else None
        })
        doc.insert(ignore_permissions=True)
        current += timedelta(days=1)


def delete_existing_entries(worker, start_date, end_date):
    frappe.db.sql("""
        DELETE FROM `tabDaily Attendance`
        WHERE worker = %s AND date BETWEEN %s AND %s
    """, (worker, start_date, end_date))


def mark_absents_for_month(worker, reference_date, source_doc=None):
    month = reference_date.month
    year = reference_date.year
    start = datetime(year, month, 1).date()
    end = datetime(year + 1, 1, 1).date() - timedelta(days=1) if month == 12 else datetime(year, month + 1, 1).date() - timedelta(days=1)

    existing_dates = set(row.date for row in frappe.get_all(
        "Daily Attendance",
        filters={"worker": worker, "date": ["between", [start, end]]},
        fields=["date"]
    ))

    current = start
    while current <= end:
        if current not in existing_dates:
            doc = frappe.get_doc({
                "doctype": "Daily Attendance",
                "worker": worker,
                "date": current,
                "status": "Absent",
                "worker_attendance": source_doc.name if source_doc else None,
                "check_in_date": source_doc.check_in_date if source_doc else None,
                "check_out_date": source_doc.check_out_date if source_doc else None
            })
            doc.insert(ignore_permissions=True)
        current += timedelta(days=1)
