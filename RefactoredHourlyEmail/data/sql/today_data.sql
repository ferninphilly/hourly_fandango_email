Use Reporting

SELECT 
	Date as Date
	,HOUR as Hour
	,Title as Title
	,ROW_NUMBER() OVER (PARTITION BY Hour ORDER BY SUM(Tickets) DESC) Rank_
	,SUM(Tickets) as Tix
	FROM dbo.AnalyticsHourlySales a with (NOLOCK)
	WHERE DATE = CAST(GETDATE() as DATE) 
	AND HOUR >= 0
	GROUP BY 
	Date
	,Hour
	,Title