
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select usd_thb
from "fuel_db"."silver"."stg_usdthb_monthly"
where usd_thb is null



  
  
      
    ) dbt_internal_test