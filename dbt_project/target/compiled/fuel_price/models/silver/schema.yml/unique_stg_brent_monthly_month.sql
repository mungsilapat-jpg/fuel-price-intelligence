
    
    

select
    month as unique_field,
    count(*) as n_records

from "fuel_db"."silver"."stg_brent_monthly"
where month is not null
group by month
having count(*) > 1


