Python Elasticsearch Log handler
********************************
This library provides an Elasticsearch logging appender compatible with the python standard `logging <https://docs.python.org/2/library/logging.html>`_ library.

This library is a fork of `https://github.com/cmanaha/python-elasticsearch-logger <https://github.com/cmanaha/python-elasticsearch-logger>`_ Thanks to Carlos Manzanedo Rueda for starting this library.

The code source is in github at `https://github.com/mkhadher/python-elasticsearch-logger <https://github.com/mkhadher/python-elasticsearch-logger>`_

Installation
============
Install using pip

.. code-block::

    pip install PYESHandler

Requirements Python 2
=====================
This library requires the following dependencies
 - elasticsearch
 - requests
 - enum

Requirements Python 3
=====================
This library requires the following dependencies
 - elasticsearch
 - requests

Additional requirements for Kerberos support
============================================
Additionally, the package support optionally kerberos authentication by adding the following dependecy
 - requests-kerberos

Additional requirements for AWS IAM user authentication (request signing)
=========================================================================
Additionally, the package support optionally AWS IAM user authentication by adding the following dependecy
 - requests-aws4auth

Using the handler in  your program
==================================
To initialise and create the handler, just add the handler to your logger as follow ::

    from pyeslogging.handlers import PYESHandler
    handler = PYESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=PYESHandler.AuthType.NO_AUTH,
                               es_index_name="my_python_index")
    log = logging.getLogger("PythonTest")
    log.setLevel(logging.INFO)
    log.addHandler(handler)

You can add fields upon initialisation, providing more data of the execution context ::

    from pyeslogging.handlers import PYESHandler
    handler = PYESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                               auth_type=PYESHandler.AuthType.NO_AUTH,
                               es_index_name="my_python_index",
                               es_additional_fields={'App': 'MyAppName', 'Environment': 'Dev'})
    log = logging.getLogger("PythonTest")
    log.setLevel(logging.INFO)
    log.addHandler(handler)

This additional fields will be applied to all logging fields and recorded in elasticsearch

To log, use the regular commands from the logging library ::

    log.info("This is an info statement that will be logged into elasticsearch")

Your code can also dump additional extra fields on a per log basis that can be used to instrument
operations. For example, when reading information from a database you could do something like::

    start_time = time.time()
    database_operation()
    db_delta = time.time() - start_time
    log.debug("DB operation took %.3f seconds" % db_delta, extra={'db_execution_time': db_delta})

The code above executes the DB operation, measures the time it took and logs an entry that contains
in the message the time the operation took as string and for convenience, it creates another field
called db_execution_time with a float that can be used to plot the time this operations are taking using
Kibana on top of elasticsearch

Initialisation parameters
=========================
The constructors takes the following parameters:
 - hosts:  The list of hosts that elasticsearch clients will connect, multiple hosts are allowed, for example ::

    [{'host':'host1','port':9200}, {'host':'host2','port':9200}]


 - auth_type: The authentication currently support PYESHandler.AuthType = NO_AUTH, BASIC_AUTH, KERBEROS_AUTH
 - auth_details: When PYESHandler.AuthType.BASIC_AUTH or "BASIC_AUTH" string is used this argument must contain a tuple of string with the user and password that will be used to authenticate against the Elasticsearch servers, for example a tuple  ('User','Password') or a dictionary {"username": "my_username","password": "my_fancy_password"}
 - aws_secret_key: When ``PYESHandler.AuthType.AWS_SIGNED_AUTH`` or "AWS_SIGNED_AUTH" string is used this argument must contain the AWS secret key of the  the AWS IAM user
 - aws_region: When ``PYESHandler.AuthType.AWS_SIGNED_AUTH`` or "AWS_SIGNED_AUTH" string is used this argument must contain the AWS region of the  the AWS Elasticsearch servers, for example ``'us-east'``
 - use_ssl: A boolean that defines if the communications should use SSL encrypted communication
 - verify_ssl: A boolean that defines if the SSL certificates are validated or not
 - buffer_size: An int, Once this size is reached on the internal buffer results are flushed into ES
 - flush_frequency_in_sec: A float representing how often and when the buffer will be flushed
 - es_index_name: A string with the prefix of the elasticsearch index that will be created. Note a date with
   YYYY.MM.dd, ``python_logger`` used by default
 - index_name_frequency: The frequency to use as part of the index naming. Currently supports
   ``ElasticECSHandler.IndexNameFrequency.DAILY``, ``ElasticECSHandler.IndexNameFrequency.WEEKLY``,
   ``ElasticECSHandler.IndexNameFrequency.MONTHLY``, ``ElasticECSHandler.IndexNameFrequency.YEARLY`` and
   ``ElasticECSHandler.IndexNameFrequency.NEVER``. By default the daily rotation is used.
   is used
 - es_doc_type: A string with the name of the document type that will be used ``python_log`` used by default
 - es_additional_fields: A dictionary with all the additional fields that you would like to add to the logs

Django Integration
==================
It is also very easy to integrate the handler to `Django <https://www.djangoproject.com/>`_ And what is even
better, at DEBUG level django logs information such as how long it takes for DB connections to return so
they can be plotted on Kibana, or the SQL statements that Django executed. ::

    from pyeslogging.handlers import PYESHandler
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': './debug.log',
                'maxBytes': 102400,
                'backupCount': 5,
            },
            'elasticsearch': {
                'level': 'DEBUG',
                'class': 'pyeslogging.handlers.PYESHandler',
                'hosts': [{'host': 'localhost', 'port': 9200}],
                'es_index_name': 'my_python_app',
                'es_additional_fields': {'App': 'Test', 'Environment': 'Dev'},
                'auth_type': PYESHandler.AuthType.NO_AUTH,
                'use_ssl': False,
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file','elasticsearch'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

There is more information about how Django logging works in the
`Django documentation <https://docs.djangoproject.com/en/1.9/topics/logging//>`_

Read logging JSON Config File
=============================
The below example can be used by a flask app or any python script. This example shows how to configure logging logger for file and elasticsearch logging using logging json config file.

``logging.json`` ::

    {
       "version":1,
       "disable_existing_loggers":true,
       "formatters":{
          "standard":{
             "format":"%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
          }
       },
       "handlers":{
          "file":{
             "level":"DEBUG",
             "class":"logging.handlers.TimedRotatingFileHandler",
             "formatter":"standard",
             "filename":"./log_file.txt",
             "when":"midnight",
             "backupCount":25
          },
          "elasticsearch":{
             "level":"DEBUG",
             "class":"pyeslogging.handlers.PYESHandler",
             "hosts": [{"host": "my.elastic.domain.com", "port": 9243}],
             "es_index_name":"PYESLogger",
             "auth_type": "BASIC_AUTH",
             "auth_details": {"username": "my_username","password": "my_fancy_password"},
             "use_ssl":true,
             "index_name_frequency": "monthly",
             "verify_ssl": true
          }
       },
       "root":{
          "handlers":[
             "file",
             "elasticsearch"
          ],
          "level":"DEBUG",
          "propagate":false
       }
    }

``app.py`` ::

    import logging
    import logging.config
    from pyeslogging.handlers import PYESHandler
    import json

    # Define logging.json path
    with open("C:\App\logging.json") as read_file:
        loggingConfigDir = json.load(read_file)
    logging.config.dictConfig(loggingConfigDir)
    logger = logging.getLogger('root')
    logger.info("Hello World !")

Building the sources & Testing
------------------------------
To create the package follow the standard python setup.py to compile.
To test, just execute the python tests within the test folder

Why using an appender rather than logstash or beats
---------------------------------------------------
In some cases is quite useful to provide all the information available within the LogRecords as it contains
things such as exception information, the method, file, log line where the log was generated.


The same functionality can be implemented in many other different ways. For example, consider the integration
using `SysLogHandler <https://docs.python.org/3/library/logging.handlers.html#sysloghandler>`_ and
`logstash syslog plugin <https://www.elastic.co/guide/en/logstash/current/plugins-inputs-syslog.html>`_.


Contributing back
-----------------
Feel free to use this as is or even better, feel free to fork and send your pull requests over.

