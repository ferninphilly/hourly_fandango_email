USE StudioReports;
SELECT 
	DayOfWeek, 
	DayNameOfWeek,
	WeekdayWeekend,
	Hour,
	Tickets,
	Cuml_Tickets,
	Pct_Tickets,
	CumPct_Tickets
FROM StudioReports.FandangoReporting.DOW_Curves;

