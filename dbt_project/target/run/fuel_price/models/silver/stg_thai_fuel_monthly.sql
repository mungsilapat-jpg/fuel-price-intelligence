
  
    

  create  table "fuel_db"."silver"."stg_thai_fuel_monthly__dbt_tmp"
  
  
    as
  
  (
    select
    date_trunc('month', obs_date)::date as month,
    item,
    avg(price_baht) as retail_price_baht,
    count(*) as n_obs
from "fuel_db"."bronze"."eppo_fuel_prices"
where country = 'TH-THAILAND'
  and price_baht is not null
group by 1, 2
  );
  