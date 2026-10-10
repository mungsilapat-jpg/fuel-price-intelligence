select
    date_trunc('month', period)::date as month,
    avg(usd_thb) as usd_thb,
    count(*) as n_days
from {{ source('bronze', 'fred_usdthb_daily') }}
where usd_thb is not null
group by 1