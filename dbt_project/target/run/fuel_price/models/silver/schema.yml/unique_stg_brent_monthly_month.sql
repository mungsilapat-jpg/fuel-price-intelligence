
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    month as unique_field,
    count(*) as n_records

from "fuel_db"."silver"."stg_brent_monthly"
where month is not null
group by month
having count(*) > 1



  
  
      
    ) dbt_internal_test