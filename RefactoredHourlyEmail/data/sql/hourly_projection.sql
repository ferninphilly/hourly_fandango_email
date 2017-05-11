use Reporting;
--select top 20* from dbo.AnalyticsHourlySales (nolock)
 --- Get date ranges (previous 365 days)
declare @minDate datetime, @maxDate datetime
set @maxDate = GETDATE() - 1
set @maxDate = convert(Date, @maxDate,20)
set @minDate = @maxDate - 365
 
if object_id('tempdb..#ModelFact') is not null drop table #ModelFact
select t.CalendarYear, t.MonthOfYear, t.CalendarQuarter, t.WeekOfYear, t.DayOfWeek, t.WeekdayWeekEnd, t.DayNameOfWeek,
          s.Date, s.Hour,
          Tickets = sum(s.Tickets)
into #ModelFact
from dbo.AnalyticsHourlySales (nolock) s
join dbo.dimDate t (nolock)  on s.Date = t.FullDate
where s.Date between @minDate and @maxDate
group by t.CalendarYear, t.MonthOfYear, t.CalendarQuarter, t.WeekOfYear, t.DayOfWeek, t.WeekdayWeekEnd, t.DayNameOfWeek,
            s.Date, s.Hour
if object_id('tempdb..#Hour') is not null drop table #Hour
select distinct Hour into #Hour from dbo.AnalyticsHourlySales (nolock) where Date between @minDate and @maxDate
 
---- Create cross join of date x hour, in case the Modelfact has hours with 0 sales (no records)
if object_id('tempdb..#ModelFact_Tmp') is not null drop table #ModelFact_Tmp
select a.*, b.*,
          Tickets = cast(0.0 as float)
into #ModelFact_Tmp
from
(select distinct FullDate as Date, CalendarYear, MonthOfYear, CalendarQuarter, WeekOfYear, DayOfWeek, DayNameOfWeek, WeekdayWeekEnd from dbo.dimDate (nolock) where FullDate between @minDate and @maxDate) a
cross join #Hour b
order by a.Date, b.Hour
 
--- Populate Modelfact ticket sales into the cross join table
update b set
Tickets = a.Tickets
from #ModelFact a, #ModelFact_Tmp b
where a.Date = b.Date and a.Hour = b.Hour
if object_id('tempdb..#ModelFact_Final') is not null drop table #ModelFact_Final
select b.*, sum(a.Tickets) as Cuml_Tickets,
          Pct_Tickets = cast(0.0 as float),
          CumPct_Tickets = cast(0.0 as float)
into #ModelFact_Final
from #ModelFact_Tmp a,
     #ModelFact_Tmp b
where a.Date = b.Date and a.Hour <= b.Hour
group by b.Date, b.CalendarYear, b.MonthOfYear, b.CalendarQuarter, b.WeekofYear, b.DayOfWeek, b.DayNameOfWeek, b.WeekdayWeekEnd, b.WeekdayWeekend, b.Hour, b.Tickets
order by b.Date, b.Hour
if object_id('tempdb..#ModelFact') is not null drop table #ModelFact
if object_id('tempdb..#ModelFact_Tmp') is not null drop table #ModelFact_Tmp
 
update b set
Pct_Tickets = round(Tickets/Total_Daily_Tickets,6),
CumPct_Tickets = round(Cuml_Tickets/Total_Daily_Tickets,6)
from
(select Date, max(Cuml_Tickets) as  Total_Daily_Tickets from #ModelFact_Final group by Date) a,
#ModelFact_Final b
where a.Date = b.Date
 
 
declare @i int, @max_i int, @min_i int
set @max_i = (select max(Hour) from #ModelFact_Final)
set @min_i = 1
set @i = @min_i
while @i <= @max_i
begin
     
       if @i = @min_i
       begin
              if object_id('tempdb..#Progressive_Curves') is not null drop table #Progressive_Curves
              select a.Date, Hour, cast(@i as int) as Current_Hour,
                        Tickets, Cuml_Tickets, Pct_Tickets, CumPct_Tickets,
                        Pct_Tickets_HTD = cast(Tickets as float)/cast(b.HTD as float),
                        CumPct_Tickets_HTD = cast(Cuml_Tickets as float)/cast(b.HTD as float)
              into #Progressive_Curves
              from #ModelFact_Final a,
                     (select Date, HTD = max(Cuml_Tickets)
                       from #ModelFact_Final
                       where Hour <= @i
                       group by Date) b
              where a.Hour <= @i
              and   a.Date = b.Date
       end
       if @i > @min_i
       begin
              insert into #Progressive_Curves
              select a.Date, Hour, cast(@i as int) as Current_Hour,
                        Tickets, Cuml_Tickets, Pct_Tickets, CumPct_Tickets,
                        Pct_Tickets_HTD = cast(Tickets as float)/cast(b.HTD as float),
                        CumPct_Tickets_HTD = cast(Cuml_Tickets as float)/cast(b.HTD as float)
              from #ModelFact_Final a,
                     (select Date, HTD = max(Cuml_Tickets)
                       from #ModelFact_Final
                       where Hour <= @i
                       group by Date) b
              where a.Hour <= @i
              and   a.Date = b.Date
       end
       set @i = @i + 1
end
/*
select * from #Progressive_Curves
order by Date, Current_Hour, Hour
*/
if object_id('tempdb..#DOW_Curves_tmp') is not null drop table #DOW_Curves_tmp
select DayOfWeek, DayNameOfWeek, WeekdayWeekend, Hour,
          Tickets = cast(sum(Tickets) as float)
into #DOW_Curves_tmp
from #ModelFact_Final
group by DayOfWeek, DayNameOfWeek, WeekdayWeekend, Hour
 
 
if object_id('tempdb..#DOW_Curves') is not null drop table #DOW_Curves
select b.DayOfWeek, b.DayNameOfWeek, b.WeekdayWeekend, b.Hour,
          b.Tickets, Cuml_Tickets = sum(a.Tickets),
          cast(null as float) as Pct_Tickets,
          cast(null as float) as CumPct_Tickets
into #DOW_Curves
from #DOW_Curves_tmp a
join #DOW_Curves_tmp b on a.DayOfWeek = b.DayOfWeek and a.Hour <= b.Hour
group by b.DayOfWeek, b.DayNameOfWeek, b.WeekdayWeekend, b.Hour, b.Tickets
update b set
Pct_Tickets = b.Tickets/a.n1,
CumPct_Tickets = b.Cuml_Tickets/a.n2
from
(select DayOfWeek, n1 = sum(Tickets), n2 = max(Cuml_Tickets) from #DOW_Curves group by DayOfWeek) a,
#DOW_Curves b
where a.DayOfWeek = b.DayOfWeek
--select * from #DOW_Curves order by DayofWeek, Hour
------------------------------
---------- Today's Forecast
------------------------------
 
declare @Today datetime
set @Today = GETDATE()
set @Today = convert(Date, @Today,20)
print @Today
 
if object_id('tempdb..#Simulation') is not null drop table #Simulation
select distinct Date, Hour, n = count(1),
       Ranking = ROW_NUMBER() over(order by Date, Hour)
into #Simulation
from
dbo.AnalyticsHourlySales (nolock)
where Date = @Today
group by Date, Hour
 
declare @Hour int, @Cutoff int, @DayofWeek int
set @Cutoff = 5
declare @j int, @max_j int, @min_j int
--set @j = 1
set @max_j = (select max(Ranking) from #Simulation)
set @j = @max_j
set @min_j = @max_j
while @j <= @max_j
begin
       set @Today = (select Date from #Simulation where Ranking = @j)
       set @Hour =  (select Hour from #Simulation where Ranking = @j)
       set @DayofWeek = (select datepart(WEEKDAY, Date) from #Simulation where Ranking = @j)
 
       if object_id('tempdb..#TodayFact_HTD') is not null drop table #TodayFact_HTD
       select t.CalendarYear, t.MonthOfYear, t.CalendarQuarter, t.WeekOfYear, t.DayOfWeek, t.WeekdayWeekEnd, t.DayNameOfWeek,
                 s.Date, s.Hour,
                 Tickets = sum(s.Tickets)
       into #TodayFact_HTD
       from dbo.AnalyticsHourlySales (nolock) s
       join dbo.dimDate t (nolock)  on s.Date = t.FullDate
       where s.Date = @Today and s.Hour <= @Hour
       group by t.CalendarYear, t.MonthOfYear, t.CalendarQuarter, t.WeekOfYear, t.DayOfWeek, t.WeekdayWeekEnd, t.DayNameOfWeek,
                     s.Date, s.Hour
       if object_id('tempdb..#TodayFact_HTD_Final') is not null drop table #TodayFact_HTD_Final
       select a.*, sum(b.Tickets) as Cuml_Tickets
       into #TodayFact_HTD_Final
       from #TodayFact_HTD a
       join #TodayFact_HTD b on a.Date = b.Date and a.Hour >= b.Hour
       group by a.CalendarYear, a.MonthOfYear, a.CalendarQuarter, a.WeekOfYear, a.DayofWeek, a.WeekdayWeekEnd, a.DayNameofWeek,
                     a.Date, a.Hour, a.Tickets
       if object_id('tempdb..#Hourly_Forecast') is not null drop table #Hourly_Forecast
       select a.*,
                 b.Pct_Tickets as DOW_Pct_Tickets,
                 b.CumPct_Tickets as DOW_CumPct_Tickets,
                 cast(null as float) as Trend_CumPct_Tickets,
                 Pct_Tickets_HTD = cast(null as float),
                 CumPct_Tickets_HTD = cast(null as float),
                 EOD_Forecast_DOW = round(a.Cuml_Tickets/b.CumPct_Tickets,0),
                 EOD_Forecast_Trend = cast(0 as int),
                 EOD_Forecast = cast(0 as int)
       into #Hourly_Forecast
       from #TodayFact_HTD_Final a
              join #DOW_Curves b on a.DayOfWeek = b.DayOfWeek and a.Hour = b.Hour
       update a set
       Pct_Tickets_HTD = round(cast(a.Tickets as float)/cast(b.d as float),6),
       CumPct_Tickets_HTD = round(cast(a.Cuml_Tickets as float)/cast(b.d as float),6)
       from #Hourly_Forecast a,
              (select d = max(Cuml_Tickets) from #Hourly_Forecast) b
       if object_id('tempdb..#MAPE') is not null drop table #MAPE
       select b.Date, b.Current_Hour,
                 MAPE = avg(abs(a.Pct_Tickets_HTD - b.Pct_Tickets_HTD)),
                 Ranking = row_number() over(order by avg(abs(a.Pct_Tickets_HTD - b.Pct_Tickets_HTD)))
       into #MAPE
       from #Hourly_Forecast a
       join #Progressive_Curves b on a.Hour = b.Hour
       where b.Current_Hour = @Hour
       group by b.Date, b.Current_Hour
 
          /*
          select * from #MAPE
          select a.*, b.Ranking
          from #Progressive_Curves a, #MAPE b
          where a.Date = b.Date and a.Current_Hour = b.Current_Hour
          and   b.Ranking <= 10
       */
 
       if object_id('tempdb..#HTD_Output') is not null drop table #HTD_Output
       select distinct b.Hour, a.Current_Hour,
                 Pct_Tickets = sum(b.Pct_Tickets*log(1.0/a.MAPE))/sum(log(1.0/a.MAPE)),
                 CumPct_Tickets = sum(b.CumPct_Tickets*log(1.0/a.MAPE))/sum(log(1.0/a.MAPE))
       into #HTD_Output
       from #MAPE a
       --join #Progressive_Curves b on a.Date = b.Date
          join #ModelFact_Final b on a.Date = b.Date
       where a.Ranking <= @CutOff --and b.Current_Hour = @Hour
       group by b.Hour, a.Current_Hour
      
       ---------------
       update b set
       Trend_CumPct_Tickets = a.CumPct_Tickets,
       EOD_Forecast_Trend = round(Cuml_Tickets/a.CumPct_Tickets,0)
       from #HTD_Output a, #Hourly_Forecast b
       where a.Hour = b.Hour
 
       declare @Wt_DOW float, @Wt_Trend float
       set @Wt_DOW = 1.0 - cast(@Hour as float)/20.00
       set @Wt_Trend = 1.0 - @Wt_DOW
       update #Hourly_Forecast set
       EOD_Forecast = round(@Wt_DOW*EOD_Forecast_DOW + @Wt_Trend*EOD_Forecast_Trend,0)
       if object_id('tempdb..#Final_Hourly_Pacing_Curves') is not null drop table #Final_Hourly_Pacing_Curves
       select DISTINCT a.Hour,
              Pct_Tickets = @Wt_DOW*a.Pct_Tickets + @Wt_Trend*b.Pct_Tickets,
                 CumPct_Tickets =  @Wt_DOW*a.CumPct_Tickets + @Wt_Trend*b.CumPct_Tickets
       into #Final_Hourly_Pacing_Curves
       from #DOW_Curves a
       join #HTD_Output b on a.Hour = b.Hour
       where a.DayOfWeek = @DayofWeek
   --    group by a.Hour
       if @j = @min_j
       begin
              if object_id('tempdb..#Simulation_Output') is not null drop table #Simulation_Output
              select a.Date, @Hour as Current_Hour, @j as Counter,
                 a.EOD_Forecast_DOW, a.EOD_Forecast_Trend, a.EOD_Forecast,
                 Actual = sum(s.Tickets),
                 FE = cast(abs(sum(s.Tickets) - a.EOD_Forecast) as float)/cast(sum(s.Tickets) as float),
                 FE_Trend = cast(abs(sum(s.Tickets) - a.EOD_Forecast_Trend) as float)/cast(sum(s.Tickets) as float),
                 FE_DOW = cast(abs(sum(s.Tickets) - a.EOD_Forecast_DOW) as float)/cast(sum(s.Tickets) as float),
                 FE_Signed = cast((sum(s.Tickets) - a.EOD_Forecast) as float)/cast(sum(s.Tickets) as float),
                 FE_Trend_Signed = cast((sum(s.Tickets) - a.EOD_Forecast_Trend) as float)/cast(sum(s.Tickets) as float),
                 FE_DOW_Signed = cast((sum(s.Tickets) - a.EOD_Forecast_DOW) as float)/cast(sum(s.Tickets) as float)
              into #Simulation_Output
              from #Hourly_Forecast a
              join dbo.AnalyticsHourlySales (nolock) s
              on a.Date = s.Date
              where a.Hour = @Hour
              group by a.Date, a.EOD_Forecast_DOW, a.EOD_Forecast_Trend, a.EOD_Forecast
 
       end
       if @j > @min_j
       begin
              insert into #Simulation_Output
              select a.Date, @Hour as Current_Hour, @j as Counter,
                 a.EOD_Forecast_DOW, a.EOD_Forecast_Trend, a.EOD_Forecast,
                 Actual = sum(s.Tickets),
                 FE = cast(abs(sum(s.Tickets) - a.EOD_Forecast) as float)/cast(sum(s.Tickets) as float),
                 FE_Trend = cast(abs(sum(s.Tickets) - a.EOD_Forecast_Trend) as float)/cast(sum(s.Tickets) as float),
                 FE_DOW = cast(abs(sum(s.Tickets) - a.EOD_Forecast_DOW) as float)/cast(sum(s.Tickets) as float),
                 FE_Signed = cast((sum(s.Tickets) - a.EOD_Forecast) as float)/cast(sum(s.Tickets) as float),
                 FE_Trend_Signed = cast((sum(s.Tickets) - a.EOD_Forecast_Trend) as float)/cast(sum(s.Tickets) as float),
                 FE_DOW_Signed = cast((sum(s.Tickets) - a.EOD_Forecast_DOW) as float)/cast(sum(s.Tickets) as float)
              from #Hourly_Forecast a
              join dbo.AnalyticsHourlySales (nolock) s
              on a.Date = s.Date
              where a.Hour = @Hour
              group by a.Date, a.EOD_Forecast_DOW, a.EOD_Forecast_Trend, a.EOD_Forecast
 
       end
 
       set @j = @j + 1
end
 

SELECT
       ho.Hour,
       ho.Pct_Tickets,
       ho.CumPct_Tickets,
       so.Actual as Actual,
       so.EOD_Forecast
FROM
       #Final_Hourly_Pacing_Curves ho
LEFT JOIN
       (SELECT * FROM #Simulation_Output
       WHERE Date = convert(date, GETDATE())
       ) so ON (ho.Hour = so.Current_Hour)
ORDER BY ho.Hour asc

 
