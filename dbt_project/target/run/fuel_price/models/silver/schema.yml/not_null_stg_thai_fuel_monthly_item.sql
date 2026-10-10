
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select item
from "fuel_db"."silver"."stg_thai_fuel_monthly"
where item is null



  
  
      
    ) dbt_internal_test