SET NOCOUNT ON
SET ANSI_WARNINGS OFF
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
USE Reporting
SELECT
	Commit_DM as PSTDate
	,SUM(Tickets) as Tickets
FROM
	Reporting.RPT.TopLineAggregate
WHERE 
	Commit_DM > convert(date, GETDATE() -35)
GROUP BY 
	Commit_DM
ORDER BY Commit_DM asc






