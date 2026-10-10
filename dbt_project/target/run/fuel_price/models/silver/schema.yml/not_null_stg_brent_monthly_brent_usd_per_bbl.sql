
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select brent_usd_per_bbl
from "fuel_db"."silver"."stg_brent_monthly"
where brent_usd_per_bbl is null



  
  
      
    ) dbt_internal_test