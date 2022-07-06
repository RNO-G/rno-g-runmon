#! /bin/sh

psql << E_O_SQL 

CREATE DATABASE rno_g_runmon; 
CREATE USER runmon; 
GRANT ALL PRIVILEGES ON DATABASE rno_g_runmon TO runmon; 

E_O_SQL
