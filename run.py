#! /usr/bin/python3 

# for sleep 
import time 
#for db connection
import psycopg2 

#for signal handler
import signal 

db_credentials="dbname=rno_g_runmon user=runmon" 

time_to_stop = False





def check_dir(db_conn, table_name, check_dir): 
    # this function will find the stations in check_dir, loop over them, 
    # find the latest run number in there with data in it, get a timestamp from a file, and insert into the database table the station number, run number, file size of last run, time of last data and current time
    # the same logic can be used for all of the different directories (ingress, rootified, outbox,archived) though ingress is probably most interesting
    print("This does nothing yet") 



def handler(signum, frame): 
    global time_to_stop
    print("Got signal ", signum) 
    time_to_stop = True 


if __name__=='__main__': 

    #set up signal handlers 
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    global time_to_stop

    #connect to database, and loop until we're told not to 
    with psycopg2.connect(db_credentials) as conn: 
        while not time_to_stop: 
            time.sleep(10) 
            check_dir(conn, "ingress","/data/ingress")
            check_dir(conn, "rootified","/data/rootified")
            check_dir(conn, "outbox","/data/outbox")
            check_dir(conn, "archived","/data/archived")


