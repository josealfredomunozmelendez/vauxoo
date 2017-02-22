------------------------------------------------------
Install all apps needed to comply with Vauxoo instance
------------------------------------------------------

This is the app module for instance vauxoo, it gathers all the dependencies
required and all the configurations that are generate specially for our
instance.

Some modules that exist for version 8.0 were deprecated and part of its logic
was extract and add it directly to this app: we set a little description for
each one of this functionalities.

Invoiceable hours in timesheet
------------------------------

We have add the next fields to the timehseet line

- Invoiceable: Invoice rate that apply to the timesheet, could be No 0%, 33%,
  50%, 80%, 85%, 90% or 100%.
- Invoiceable Hours: Is a compute field that let us now the quantity that will
  be invoiced taking into account the real duration and the invoice rate.
- Invoice: The invoice related to the timesheet line.

This fields are visibile for the user on the tree view of timehseet lines
(account.analytic.line)

**NOTE:** I take part of odoo/hr_timehseet_invoice and addons-vauxoo/user_story
8.0 modules to be able to have this functionality.

Timesheet Reports
-----------------

Timesheet reports used internally: A way to report timesheet's consumption of
time. This ones were migrated only the basic, not completed migrate from api.
With this functionality we can:

    1. Wizard to report timesheets to deliver to customers well presented and
    correctly ordered and audited.

        a. Filter between dates.
        b. Group by month, by user or by analytic account.

    2. Improve your communication to your customers delivering directly this
    report.

    3. Save your reports to use them as auditory process.

**NOTE:** Functionality partially migrated from hr_timesheet_report 8.0. All
the references to user story model were deleted.

User from Employee
==================

This adds a menu option, which allow to link an user based on an
employee already created.

A Wizard is launched, which show an option in order to choose a group, which
will be used to link a user, using his data stored already.
