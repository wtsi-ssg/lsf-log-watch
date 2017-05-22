*THIS IS A WORK IN PROGESS*
===========================

```
IBM Platform LSF is a powerful workload management platform for demanding, 
distributed HPC environments. It provides a comprehensive set of intelligent,
policy-driven scheduling features that enable you to utilise all of your 
compute infrastructure resources and ensure optimal application performance.

Obtaining job status is usually via poll based bjobs requests. As clusters and
user numbers continue to grow, this process becomes limiting and not a 
practical programmtic interface for workload management, pipeline development
or cluster monitoring.

This script should provide job data directly from the lsb.acct file. All 
LSF status data is captured, along with job resource usage and requirements, 
which are sent to an AMQP queue.
```

Setup
=====

```
The lsf_log_watch.py script requires a host running LSF 9.x with read access 
to lsb.streams and the IBM platform python api installed. 

A functioning Rabbit AMQP server with configured accounts and basic queue 
in place. The AMQP setup is outside the scope here.

The platform python LSF api is available from here:
https://github.com/PlatformLSF/platform-python-lsf-api

Outside of basic modules the script also requires:

pika
pygtail
```

Recommended run methodology
==========================

Configure virtualenv
--------------------

```
Install virtualenv within your local environment and add the required python
lsf api, pika, etc modules to your virtualenv. NB pythonlsf requires lsf 
headers and libraries to be available on the host for installation to succeed.

python lsf documetnation can be found here:
https://github.com/PlatformLSF/platform-python-lsf-api

source and confirm that these work as expected with:

source <virtualenv_dir>/bin/activate

Edit lsf_log_watch.py to reflect local lsb.acct location and AMQP server 
connection details and credentials.

run ./lsf_log_watch.py &
```

Example reader
-----------------------

```
Please refer to www.rabbitmq.com for AMQP consumer example code. Examples
are provided for Python and Java.
```
