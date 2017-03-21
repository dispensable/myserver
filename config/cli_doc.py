# -*- coding:utf-8 -*-

from docopt import docopt

CLI_DOC = """MyServer.
Usage:
  myserver [options] [-e <KEY=VALUE>...] [--proxy-allow-from PROXY_ALLOW_IPS...] [--bind ADDRESS...] <module> <app>

Options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --proxy-protocol      Enable detect PROXY protocol (PROXY mode). [default: False]
  --worker-connections INT
                        The maximum number of simultaneous clients. [default: 1000]
  --statsd-host STATSD_ADDR
                        ``host:port`` of the statsd server to log to..
  --max-requests-jitter INT
                        The maximum jitter to add to the *max_requests*
                        setting. [default: 0]
  --error-logfile FILE --log-file=FILE
                        The Error log file to write to. [default: -]
  -R --enable-stdio-inheritance
                        Enable stdio inheritance. [default: False]
  -k STRING --worker-class=STRING
                        The type of workers to use. [default: sync]
  --ssl-version SSL_VERSION
                        SSL version to use (see stdlib ssl module's) [default: 2]
  --suppress-ragged-eofs
                        Suppress ragged EOFs (see stdlib ssl module's) [default: True]
  --log-syslog          Send  MyServer* logs to syslog. [default: False]
  --log-syslog-facility SYSLOG_FACILITY
                        Syslog facility name [default: user]
  --cert-reqs CERT_REQS
                        Whether client certificate is required (see stdlib ssl
                        module's) [default: 0]
  --preload             Load application code before the worker processes are
                        forked. [default: False]
  --keep-alive INT      The number of seconds to wait for requests on a Keep-
                        Alive connection. [default: 2]
  --access-logfile FILE
                        The Access log file to write to.
  -g GROUP --group=GROUP
                        Switch worker process to run as this group. [default: 20]
  --graceful-timeout INT
                        Timeout for graceful workers restart. [default: 30]
  --do-handshake-on-connect
                        Whether to perform SSL handshake on socket connect
                        (see stdlib ssl module's) [default: False]
  --spew                Install a trace function that spews every line
                        executed by the server. [default: False]
  -w INT --workers=INT
                        The number of worker processes for handling requests.
                        [default: 1]
  -n STRING --name=STRING
                        A base to use with setproctitle for process naming.
.
  --no-sendfile         Disables the use of ``sendfile()``..
  -p FILE --pid=FILE   A filename to use for the PID file..
  -m INT --umask=INT   A bit mask for the file mode on files written by
                     MyServer. [default: 0]
  --worker-tmp-dir DIR  A directory to use for the worker heartbeat temporary
                        file..
  --limit-request-fields INT
                        Limit the number of HTTP headers fields in a request.
                        [default: 100]
  --pythonpath STRING   A comma-separated list of directories to add to the
                        Python path..
  -c CONFIG --config=CONFIG
                        The MyServer config file..
  --log-config FILE     The log config file to use..
  --check-config        Check the configuration. [default: False]
  --statsd-prefix STATSD_PREFIX
                        Prefix to use when emitting statsd metrics (a trailing
                        ``.`` is added, [default: '']
  --reload-engine STRING
                        The implementation that should be used to power
                        :ref:`reload`. [default: auto]
  --proxy-allow-from PROXY_ALLOW_IPS
                        Front-end's IPs from which allowed accept proxy
                        requests (comma separate). [default: 127.0.0.1]
  --forwarded-allow-ips STRING
                        Front-end's IPs from which allowed to handle set
                        secure headers. [default: 127.0.0.1]
  --threads INT         The number of worker threads for handling requests.
                        [default: 1]
  --max-requests INT    The maximum number of requests a worker will process
                        before restarting. [default: 0]
  --chdir CHDIR         Chdir to specified directory before apps loading.
                        [default: /Users/apple]
  -D --daemon          Daemonize the MyServer process. [default: False]
  -u USER --user=USER  Switch worker processes to run as this user. [default: 501]
  --limit-request-line INT
                        The maximum size of HTTP request line in bytes. [default: 4094]
  --access-logformat STRING
                        The access log format. [default: %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"]
  --certfile FILE       SSL certificate file.
  --paste STRING, --paster=STRING
                        Load a PasteDeploy config file. The argument may
                        contain a ``#``.
  --log-syslog-to SYSLOG_ADDR
                        Address to send syslog messages.
                        [default: unix:///var/run/syslog]
  --log-syslog-prefix SYSLOG_PREFIX
                        Makes MyServer use the parameter as program-name in
                        the syslog entries..
  --ciphers CIPHERS     Ciphers to use (see stdlib ssl module's) [default: TLSv1]
  --log-level LEVEL     The granularity of Error log outputs. [default: info]
  -b ADDRESS --bind=ADDRESS
                        The socket to bind. [default: 127.0.0.1:8000]
  -e <KEY=VALUE> --env=<KEY=VALUE>     Set environment variable (key=value). [default: '']
  --initgroups          If true, set the worker process's group access list
                        with all of the [default: False]
  --capture-output      Redirect stdout/stderr to Error log. [default: False]
  --reload              Restart workers when code changes. [default: False]
  --limit-request-field_size INT
                        Limit the allowed size of an HTTP request header
                        field. [default: 8190]
  -t INT --timeout=INT
                        Workers silent for more than this many seconds are
                        killed and restarted. [default: 30]
  --keyfile FILE        SSL key file.
  --ca-certs FILE       CA certificates file.
  --backlog INT         The maximum number of pending connections. [default: 2048]
  --logger-class STRING
                        The logger you want to use to log events in MyServer.
                        [default: myserver.glogging.Logger]
"""

if __name__ == '__main__':

    arguments = docopt(CLI_DOC, version='0.1.0')
    print(arguments)
