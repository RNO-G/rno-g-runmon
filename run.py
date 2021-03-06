#! /usr/bin/python3 

# for sleep 
import time 
#for db connection
import psycopg2 
import pathlib,os,datetime,glob
#for signal handler
import signal 
import numpy as np

db_credentials="dbname=rno_g_runmon user=runmon" 

time_to_stop = False


def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def check_dir(db_conn, table_name, check_dir): 
    # this function will find the stations in check_dir, loop over them, 
    stnp=glob.glob(check_dir+'/station*')
    stations=[]
    for s in stnp: stations.append(str(s)[-2:])
    stations.sort(key=int)
    stations=[str(x) for x in stations]
    #these indices will correspond to the respective stations in future arrays
    latrunpath=[] #path to each latest run
    latruns=[] #num of latest run for each station
    tmstp=[] #timestamp of latest run
    fsize=[] #size of run file

    #this grabs the path of the last modified run for each station & its timestamp
    print(table_name)
    for stn in stations:
            print(max(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'), key=os.path.getmtime))
            latrunpath.append(str(max(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'), key=os.path.getmtime)))
            print(datetime.datetime.fromtimestamp(os.path.getmtime(max(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'), key=os.path.getmtime))))
            tmstp.append(datetime.datetime.fromtimestamp(os.path.getmtime(max(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'), key=os.path.getmtime))))

    #this grabs the name of the run directory and the combined size of all files within  
    for pt in latrunpath:
        latruns.append(pt.split(os.sep)[-1]) #name of each run
        fsize.append((np.round(float(get_dir_size(pt)/1024),2))) #total file size kb


    #pre-existing titles in the database table: [station_number, run_num,time_mod, time_accessed,size_kb]

    ## SQL SECTION STARTS HERE ##################
    cursor = db_conn.cursor()
    try:
    #    cursor = db_conn.cursor()

        #one entry for each station
        for i in range(len(stations)):
            q="INSERT INTO "+table_name+" (station,run,time_mod,time_now,size_kb) VALUES (%s,%s,%s,%s,%s) RETURNING id;"
            qval=('station'+stations[i], str(latruns[i]),str(tmstp[i]),str(datetime.datetime.now()),fsize[i])

            cursor.execute(q,qval) #insert entry into table

            db_conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert data\nError: ", error)

    finally:
        if db_conn:
            cursor.close()
#            db_conn.close()
            print("PostgreSQL connection is closed")
    
    ##SQL SECTION ENDS HERE #######################
    print("This almost does something!") 



def handler(signum, frame): 
    global time_to_stop
    print("Got signal ", signum) 
    time_to_stop = True 


if __name__=='__main__': 

    #set up signal handlers 
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    time_to_stop

    #connect to database, and loop until we're told not to 
    with psycopg2.connect(db_credentials) as conn: 
        while not time_to_stop: 
            check_dir(conn, "ingress","/data/ingress")
            check_dir(conn, "rootified","/data/rootified")
            check_dir(conn, "archived","/data/archived")
            check_dir(conn, "outbox","/data/outbox")
            time.sleep(30)

