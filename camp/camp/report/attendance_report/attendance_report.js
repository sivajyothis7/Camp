// Copyright (c) 2025, siva and contributors
// For license information, please see license.txt


frappe.query_reports["Attendance Report"] = {
    filters: [
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { "value": "1", "label": "January" },
                { "value": "2", "label": "February" },
                { "value": "3", "label": "March" },
                { "value": "4", "label": "April" },
                { "value": "5", "label": "May" },
                { "value": "6", "label": "June" },
                { "value": "7", "label": "July" },
                { "value": "8", "label": "August" },
                { "value": "9", "label": "September" },
                { "value": "10", "label": "October" },
                { "value": "11", "label": "November" },
                { "value": "12", "label": "December" }
            ],
            default: (new Date()).getMonth() + 1
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Int",
            default: new Date().getFullYear()
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        const fieldname = column.fieldname;

        if (fieldname && /^day_\d+$/.test(fieldname)) {
            if (value === "A") {
                return `<span style="color: red !important; font-weight: bold;">${value}</span>`;
            } else if (value === "P") {
                return `<span style="color: green !important; font-weight: bold;">${value}</span>`;
            } else if (value === "V") {
                return `<span style="color: orange !important; font-weight: bold;">${value}</span>`;
            }
        }

        return default_formatter(value, row, column, data);
    }
};
