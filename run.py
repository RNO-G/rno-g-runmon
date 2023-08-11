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


def check_dir(table_name, check_dir):
    stnp=glob.glob(check_dir+'/station*')
    stations=[]
    for s in stnp: stations.append(str(s)[-2:])
    stations.sort(key=int)
    stations=[str(x) for x in stations]
    #these indices will correspond to the respective stations in future arrays
    lrp=[]  #paths to latest run per station
    slrp=[] #paths to second-to-last run per station
    latruns=[] #num of latest run for each station
    tmstp=[] #timestamps of latest run
    fsize=[] #sizes of run files

    #this grabs the path of the last modified run for each station & its timestamp
    print(table_name)
    #os.mkdir(check_dir+'/station'+stations[0]+'/run_abc')
    #print('Create directory: run_abc')
    for stn in stations:
            #print('===============\nStation {}'.format(stn))
            lr = [str(x) for x  in list(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'))]
            lrp.append(str(max(lr, key=os.path.getmtime)))
            slr = lr.copy()
            slr.remove(lrp[-1])            
            slrp.append(str(max(slr, key=os.path.getmtime)))
            #print(datetime.datetime.fromtimestamp(os.path.getmtime(max(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'), key=os.path.getmtime))))
            tmstp.append(datetime.datetime.fromtimestamp(os.path.getmtime(max(pathlib.Path(check_dir+'/station'+stn+'/').glob('run*/'), key=os.path.getmtime))))
            #print('Last path: {}'.format(lrp))
            #print('2nd last path: {}'.format(slrp))
    #print('==================\n')


    #os.rmdir(check_dir+'/station'+stations[0]+'/run_abc')
    #print('Delete directory: run_abc')
    #this grabs the name of the run directory and the combined size of all files within
    for ip,pt in enumerate(lrp):
        try:
            fsize.append((np.round(float(get_dir_size(pt)/1024),2))) #total file size kb
            latruns.append(pt.split(os.sep)[-1]) #name of each run

        except FileNotFoundError:
            print('Path ({}) was not found, resorting to second most recent run'.format(pt))
            fsize.append((np.round(float(get_dir_size(slrp[ip])/1024),2)))
            latruns.append(slrp[ip].split(os.sep)[-1]) 
    #print('\n\ncollected recent runs: {}'.format(latruns))
    #print('collected recent run sizes: {}'.format(fsize))
            

    #pre-existing titles in the database table: [station_number, run_num,time_mod, time_accessed,size_kb]
    ## SQL SECTION STARTS HERE ##################
    cursor = db_conn.cursor()
    try:
       # cursor = db_conn.cursor()

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
            #db_conn.close()
            #print("PostgreSQL connection is closed")

    ##SQL SECTION ENDS HERE #######################

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
            check_dir("ingress","/data/ingress")
            check_dir("rootified","/data/rootified")
            check_dir("archived","/data/archived")
            check_dir("outbox","/data/outbox")
            time.sleep(30)
