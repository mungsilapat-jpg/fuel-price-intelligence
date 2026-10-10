select
    date_trunc('month', period)::date as month,
    avg(value) as brent_usd_per_bbl,
    count(*) as n_days
from "fuel_db"."bronze"."eia_brent_daily"
where value is not null
group by 1