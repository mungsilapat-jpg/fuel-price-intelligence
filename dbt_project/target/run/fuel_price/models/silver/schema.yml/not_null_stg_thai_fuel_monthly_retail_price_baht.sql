
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select retail_price_baht
from "fuel_db"."silver"."stg_thai_fuel_monthly"
where retail_price_baht is null



  
  
      
    ) dbt_internal_test