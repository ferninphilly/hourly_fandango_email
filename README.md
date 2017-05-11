README.md

######Hourly Report######

This is the README for the hourly report for Fandango.com. I will be covering all of the aspects that go into the hourly report here, including issues with updating and re-formatting the report as necessary. 

##The YAML:##

The first thing to understand about this report is that just about every change that you might want to make is contined in the hourly.yaml file which is located here: 

* Refactored Hourly/
	* data/
		* yaml/
			* hourly.yaml

The yaml contains the username and password data, testing, folder locations, etc

Here is the basic format for that:
```python

hourly_report:
    connection_data:
        host: FANDSINSQL002
        user: *************
        password: ************
        database: Reporting
    file_locations:
        today_data: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/sql/today_data.sql
        month_ttl: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/sql/month_ttl.sql
        channel: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/sql/channel.sql
        baseline: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/excel/baseline.xlsx
        hourlysmooth: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/excel/hourlysmooth.xlsx
        pctSmoothing: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/excel/pctSmoothing.xlsx
        acct_proc: ACCT.rpt.hourlyReportProc
        dow_curve: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/sql/dow_curve.sql
        hourly_proc: ACCT.rpt.DailyHourlyReportProc
        hourly_projection: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/data/sql/hourly_projection.sql
        recipients: /Users/fpombeiro/Projects/hourly_email/RefactoredHourlyEmail/email_module/recipients/recipients.csv
        testing: True

```

So a basic key/value store-- but please keep the key names at all times if you change values.

So if, for instance, you wanted to change the status from *active* to *testing* - thereby limiting the report to only go to selected people-- simply change the "testing" parameter.

##How do I update recipients and/or CIF?##
The **recipients file** is a .csv that is contained in the shared directory **//colfsrp01/BIAnalyticsReporting/hourly_report_data/recipients/recipients.csv**
To add a recipient simply open that csv, add the email address of the user to the bottom of the csv, and close it again. 
The CIF file is a .xlsx that is contained in the shared directory **//colfsrp01/BIAnalyticsReporting/hourly_report_data/cif_data/baseline.xlsx**

_Note that the format of these files **should never** be changed or it will break the report!! So please- if you add data- make sure that you keep the reports in the same format (and save a file to the **//colfsrp01/BIAnalyticsReporting/hourly_report_data/bkup/** folder that I have there for keeping the original **before** you change it!)_

##Troubleshooting:##
Obviously- start with emailing BIENG@ if there is a problem with the report. If you want to go into the server that is running the hourly report go to:
```
ssh fernbi@10.56.89.9

```
...and enter a password. 
The report itself is found in the ~/refactored_hourly directory.
There is a file in the highest level directory called *~/refactored_hourly/RefactoredHourlyEmail/kill_cached_data.py*. Most problems with the report can be fixed by going in to that file (located in RefactoredHourlyEmail) and running:
```python

python ~/refactored_hourly/RefactoredHourlyEmail/kill_cached_data.py

```

####The Framework:####
The hourly report is set up in modules that are spelled out as follows:
 Ulitmately the whole thing is driven by the __main__.py file in the top level "RefactoredHourly" directory. The setup is similar to a standard "MVC" framework- with the "Data" directory/module being the model, the controller being the "Transformations" directory and the view being the "Visualize" directory.



