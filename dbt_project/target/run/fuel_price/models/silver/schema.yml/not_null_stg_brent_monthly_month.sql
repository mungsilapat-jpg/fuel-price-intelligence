
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select month
from "fuel_db"."silver"."stg_brent_monthly"
where month is null



  
  
      
    ) dbt_internal_test