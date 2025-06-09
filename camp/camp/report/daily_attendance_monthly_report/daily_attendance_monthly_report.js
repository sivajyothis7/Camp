// Copyright (c) 2025, siva and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Attendance Monthly Report"] = {
    "filters": [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": [
                {"value": "January", "label": __("January")},
                {"value": "February", "label": __("February")},
                {"value": "March", "label": __("March")},
                {"value": "April", "label": __("April")},
                {"value": "May", "label": __("May")},
                {"value": "June", "label": __("June")},
                {"value": "July", "label": __("July")},
                {"value": "August", "label": __("August")},
                {"value": "September", "label": __("September")},
                {"value": "October", "label": __("October")},
                {"value": "November", "label": __("November")},
                {"value": "December", "label": __("December")}
            ],
            "default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).toLocaleString('default', { month: 'long' }),
            "reqd": 1
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": frappe.datetime.get_today().split("-")[0],
            "reqd": 1
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color the day columns based on status
        if (column.id && !isNaN(column.id)) {
            if (value.includes('P</span>')) {
                value = value.replace('style="', 'style="font-weight:bold; ');
            } else if (value.includes('V</span>')) {
                value = value.replace('style="', 'style="font-weight:bold; ');
            } else if (value.includes('CO</span>')) {
                value = value.replace('style="', 'style="font-weight:bold; ');
            }
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add any custom onload functionality here
    }
};