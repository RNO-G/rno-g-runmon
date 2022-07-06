#! /bin/sh 

read -r -p "Are you sure? This will nuke the database (type \"DO IT LIVE!\" to confirm): " response
if [[ "$response" == "DO IT LIVE!" ]] 
then 

  echo "DOING IT LIVE! (goodbye data...)"

psql rno_g_runmon << E_O_SQL

DROP TABLE if exists ingress; 
DROP TABLE if exists rootified; 
DROP TABLE if exists archived; 
DROP TABLE if exists outbox; 


CREATE TABLE ingress ( 
row_id SERIAL PRIMARY KEY, 
station_number integer not null,
last_run integer not null,
run_size integer not null,
run_update_time timestamp not null,
insert_time  timestamp not null
); 

CREATE TABLE rootified ( 
row_id SERIAL PRIMARY KEY, 
station_number integer not null,
last_run integer not null,
run_size integer not null,
run_update_time timestamp not null,
insert_time  timestamp not null
); 

CREATE TABLE archived ( 
row_id SERIAL PRIMARY KEY, 
station_number integer not null,
last_run integer not null,
run_size integer not null,
run_update_time timestamp not null,
insert_time  timestamp not null
); 

CREATE TABLE outbox ( 
row_id SERIAL PRIMARY KEY, 
station_number integer not null,
last_run integer not null,
run_size integer not null,
run_update_time timestamp not null,
insert_time  timestamp not null
); 



E_O_SQL

else
  echo "bwak bwak" 
fi 

