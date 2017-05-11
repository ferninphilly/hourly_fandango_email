USE Reporting
SELECT
	Date
	,Hour
	,Channel as Title
	,SUM(Tickets) as Tix
FROM
	Reporting.dbo.AnalyticsHourlySales (NOLOCK)
WHERE Date = CONVERT(DATE, GETDATE())
GROUP BY
	Date
	,Hour
	,Channel;