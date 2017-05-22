#!/usr/bin/env python

'''
################################################################################
# Copyright (c) 2013, 2016 Genome Research Ltd. 
# 
# Author: Peter Clapham <pc7@sanger.ac.uk>
# 
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU Affero General Public License as published by the Free 
# Software Foundation; either version 3 of the License, or (at your option) any 
# later version. 
# 
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more 
# details. 
# 
# You should have received a copy of the GNU Affero General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>. 
################################################################################


This script is documented within the associated README.md.
They are provided as a skeleton starting point for other 
projects.
'''

import pika
import json
import time
import logging
from pygtail import Pygtail
from pythonlsf import lsf

def display(eventrec):
    '''
    collect event records
    '''
    idx = eventrec.eventLog.jobFinishLog.idx
    jobId = eventrec.eventLog.jobFinishLog.jobId
    queue = eventrec.eventLog.jobFinishLog.queue
    avgMem = eventrec.eventLog.jobFinishLog.avgMem
    resReq = eventrec.eventLog.jobFinishLog.resReq
    options = eventrec.eventLog.jobFinishLog.options
    jStatus = eventrec.eventLog.jobFinishLog.jStatus
    maxRMem = eventrec.eventLog.jobFinishLog.maxRMem
    jobName = eventrec.eventLog.jobFinishLog.jobName
    endTime = eventrec.eventLog.jobFinishLog.endTime
    runTime = eventrec.eventLog.jobFinishLog.runTime
    cpuTime = eventrec.eventLog.jobFinishLog.cpuTime
    runLimit = eventrec.eventLog.jobFinishLog.runLimit
    userName = eventrec.eventLog.jobFinishLog.userName
    exitInfo = eventrec.eventLog.jobFinishLog.exitInfo
    termTime = eventrec.eventLog.jobFinishLog.termTime
    startTime = eventrec.eventLog.jobFinishLog.startTime
    exitStatus = eventrec.eventLog.jobFinishLog.exitStatus
    exceptMask = eventrec.eventLog.jobFinishLog.exceptMask
    numProcessors = eventrec.eventLog.jobFinishLog.numProcessors
    numExHosts = eventrec.eventLog.jobFinishLog.numExHosts

    #execHosts are an array, we can get array number from
    #numExHosts and iterate through the set to create an
    #execHosts (hosts) per job
    
    hosts = ""
    execHosts = eventrec.eventLog.jobFinishLog.execHosts
    for i in range(0,numExHosts):
        hosts += lsf.stringArray_getitem(execHosts, i) + " "

    # Some exit codes are special. A quick lookup.
    if exitStatus == 256:
        exitStatus = 1
    if exitStatus == 512:
        exitStatus = 0
    if exitStatus == 158:
        exitStatus = 30

    # some have bit shifts
    if exitStatus != 256 and exitStatus != 158 \
	and exitStatus != 512 and exitStatus > 255:
        exitStatus = bintrans(exitStatus)

    # lookup LSF kill reasons, where they exist
    if 1 <= exitInfo <= 26:
        exitInfo = whyexit(exitInfo)

    GMendTime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(endTime))

    mkmessage(idx, jobId, queue, avgMem, options, resReq, jStatus, \
			  maxRMem, jobName, endTime, runTime, cpuTime, runLimit, \
			  userName, exitInfo, termTime, startTime, exitStatus, \
			  exceptMask, numProcessors, GMendTime, hosts)


def mkmessage(idx, jobId, queue, avgMem, options, resReq, jStatus, \
			  maxRMem, jobName, endTime, runTime, cpuTime, runLimit, \
			  userName, exitInfo, termTime, startTime, exitStatus, \
			  exceptMask, numProcessors, GMendTime, hosts):
    '''
    Collate data ready for sending as a single data set
    '''

    message = {}
    if exitStatus != 0:
        job = "Failed"
    else:
        job = "Success"

    data = [job, jobId, idx, queue, avgMem, options, resReq, jStatus, \
		   maxRMem, jobName, endTime, runTime, cpuTime, runLimit, \
		   userName, exitInfo, termTime, startTime, exitStatus, \
		   exceptMask, numProcessors, GMendTime, hosts]
    allsets = ["job", "jobId", "idx", "queue", "avgMem", "options", \
			    "resReq", "jStatus", "maxRMem", "jobName", "endTime", \
			    "runTime", "cpuTime", "runLimit", "userName", \
			    "exitInfo", "termTime", "startTime", "exitStatus", \
			    "exceptMask", "numProcessors", "GMendTime", "Exhosts"]
			    
    datadict = dict(zip(allsets, data))

    if idx == 0:
        del(datadict["idx"])

    send(datadict)

def send(datadict):
    '''
    connect to rabbitmq and send jmessage
    '''
    logging.getLogger('pika').setLevel(logging.DEBUG)

    # Set correct connection details here
    credentials = pika.credentials.PlainCredentials("user", "passwd")
    parameters = pika.ConnectionParameters('amqp-srv-server',
                                            5672,
                                            '/',
                                            credentials)
    connection = pika.adapters.blocking_connection.BlockingConnection\
				(parameters=parameters)

    channel = connection.channel()
    channel.queue_declare(queue='Finish')
    channel.basic_publish(exchange='',
                          routing_key='Finish',
                          body=json.dumps(datadict))
    connection.close()

def bintrans(exitStatus):
    '''
    Why does lsf sometimes add bit shift to
    it's exit codes ? Here's a tidy up to 
    rectify the problem
    '''
    binadjustexitStatus = bin(exitStatus).rstrip("0")
    exitreturn = int(binadjustexitStatus, 2)
    return exitreturn

def whyexit(exitInfo):
    '''
    LSF exitInfo gives hints as to why the job was killed.
    These are the lookups provided by LSF
    '''

    errs = {0: "job exited, reason unknown TERM_UNKNOWN",  
            1: "job killed after preemption TERM_PREEMPT", 
            2: "job killed after queue run window is closed TERM_WINDOW",
            3: "job killed after load exceeds threshold TERM_LOAD",
            4: "job exited, reason unknown TERM_OTHER", 
            5: "job killed after reaching LSF run time limit TERM_RUNLIMIT",
            6: "job killed after deadline expires TERM_DEADLINE", 
            7: "job killed after reaching LSF process TERM_PROCESSLIMIT", 
            8: "job killed by owner without time for cleanup TERM_FORCE_OWNER", 
            9: "job killed by root or LSF administrator without time for cleanup TERM_FORCE_ADMIN", 
            10: "job killed and requeued by owner TERM_REQUEUE_OWNER", 
            11: "job killed and requeued by root or LSF administrator TERM_REQUEUE_ADMIN", 
            12: "job killed after reaching LSF CPU usage limit TERM_CPULIMIT", 
            13: "job killed after checkpointing TERM_CHKPNT", 
            14: "job killed by owner TERM_OWNER", 
            15: "job killed by root or an administrator TERM_ADMIN", 
            16: "job killed after reaching LSF memory usage limit TERM_MEMLIMIT", 
            17: "job killed by a signal external to lsf TERM_EXTERNAL_SIGNAL", 
            18: "job terminated abnormally in RMS TERM_RMS", 
            19: "job killed when LSF is not available TERM_ZOMBIE", 
            20: "job killed after reaching LSF swap usage limit TERM_SWAP", 
            21: "job killed after reaching LSF thread TERM_THREADLIMIT", 
            22: "job terminated abnormally in SLURM TERM_SLURM", 
            23: "job exited, reason unknown TERM_BUCKET_KILL", 
            24: "job terminated after control PID died TERM_CTRL_PID", 
            25: "Current working directory is not accessible or does not exist on the execution host TERM_CWD_NOTEXIST", 
            26: "hung job removed from the LSF system TERM_REMOVE_HUNG_JOB"}

    whyerror = errs[exitInfo]
    return whyerror

def read_eventrec(path):
    '''
    read lsb.acct
    '''
    while True:
        for line in Pygtail(path, offset_file="lsb.acct.pygtail", paranoid=True):
            log = lsf.eventRec()
            result = lsf.lsb_geteventrecbyline(line, log)
            if result != 0:
		time.sleep(2)
                break
            display(log)

        time.sleep(1)
        
if __name__ == '__main__':
    # Set correct path to lsb.acct here
    read_eventrec("/usr/local/lsf/work/<cluster_name>/logdir/lsb.acct")
