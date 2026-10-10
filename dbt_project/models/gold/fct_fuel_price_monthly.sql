with fuel as (
    select month, item, retail_price_baht
    from {{ ref('stg_thai_fuel_monthly') }}
),

brent as (
    select month, brent_usd_per_bbl
    from {{ ref('stg_brent_monthly') }}
),

fx as (
    select month, usd_thb
    from {{ ref('stg_usdthb_monthly') }}
),

joined as (
    select
        f.month,
        f.item,
        f.retail_price_baht,
        b.brent_usd_per_bbl,
        x.usd_thb,
        b.brent_usd_per_bbl * x.usd_thb / 158.987 as brent_baht_per_litre
    from fuel f
    inner join brent b on f.month = b.month
    inner join fx x on f.month = x.month
)

select
    *,
    lag(retail_price_baht, 1) over (partition by item order by month) as retail_price_lag1,
    lag(brent_baht_per_litre, 1) over (partition by item order by month) as brent_baht_per_litre_lag1,
    lag(brent_baht_per_litre, 2) over (partition by item order by month) as brent_baht_per_litre_lag2,
    lag(brent_baht_per_litre, 3) over (partition by item order by month) as brent_baht_per_litre_lag3
from joined