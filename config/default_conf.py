# -*-coding:utf-8 -*-

import sys

# app
app = None

# module
module = None

# default config in file

access_logfile = None
access_logformat = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# The maximum number of pending connections.
backlog = 2048

# The socket to bind.
bind = '127.0.0.1:8000'

ca_certs = None
capture_output = False
cert_reqs = 0
certfile = None
chdir = '/Users/apple'
check_config = False
ciphers = 'TLSv1'

# The Myserver config file.
config = None

daemon = False
do_handshake_on_connect = False
enable_stdio_inheritance = False
env = []
forwarded_allow_ips = '127.0.0.1'

# Timeout for graceful workers restart.
graceful_timeout = 30


group = 20
help = False
initgroups = False

# The number of seconds to wait for requests on a Keep-Alive connection.
keep_alive = 2


keyfile = None

# Limit the allowed size of an HTTP request header field.
limit_request_field_size = 8190

# Limit the number of HTTP headers fields in a request.
limit_request_fields = 100

# The maximum size of HTTP request line in bytes.
limit_request_line = 4094
log_config = None
log_file = sys.stderr
log_level = 'info'
log_syslog = False
log_syslog_facility = 'user'
log_syslog_prefix = None
log_syslog_to = 'unix:///var/run/syslog'
logger_class = 'myserver.glogging.Logger'

# The maximum number of requests a worker will process before restarting.
max_requests = 0

# The maximum jitter to add to the *max_requests* setting.
max_requests_jitter = 0


name = None
no_sendfile = False
paster = None
pid = None
preload = True
proxy_allow_from = '127.0.0.1'
proxy_protocol = False
pythonpath = None

# Restart workers when code changes.
reload = True

# The implementation that should be used to power :ref:`reload`.
reload_engine = 'auto'
spew = False
ssl_version = 3
statsd_host = None
statsd_prefix = ""
suppress_ragged_eofs = False

# The number of worker threads for handling requests.
threads = 1

# Workers silent for more than this many seconds are killed and restarted.
timeout = 30


umask = 0
user = 501
version = False

# The type of workers to use
worker_class = 'sync'

# The maximum number of simultaneous clients.
worker_connections = 1000


worker_tmp_dir = None

# The number of worker processes for handling requests.
workers = 4

# 临时请求数据存放目录
tmp_upload_dir = None

# A dictionary containing headers and values that the front-end proxy
# uses to indicate HTTPS requests. These tell myserver to set
# ``wsgi.url_scheme`` to ``https``, so your application can tell that the
# request is secure.

secure_scheme_headers = {
        "X-FORWARDED-PROTOCOL": "ssl",
        "X-FORWARDED-PROTO": "https",
        "X-FORWARDED-SSL": "on"
}

# 默认进程名
default_proc_name = 'myserver'


# 服务器启动时的钩子
def on_staring(server):
    pass
on_staring_hook = on_staring


# 服务器重新载入时的钩子
def on_reload(server):
    pass
on_reload_hook = on_reload


# 服务器启动之后的钩子
def when_booted(server):
    pass
on_booted_hook = when_booted


# worker fork 前的钩子
def before_worker_fork(server, worker):
    pass
before_fork_worker = before_worker_fork


# worker fork之后的钩子
def after_worker_forked(server, worker):
    pass
after_worker_fork = after_worker_forked


# worker初始化完成后的钩子
def after_worker_init(worker):
    pass
after_worker_inited = after_worker_init

# before worker init
def before_worker_init():
    pass

before_worker_init = before_worker_init


# worker 因信号SIGINT 或者 SIGQUIT 退出之后钩子
def worker_ini(worker):
    pass
after_worker_quit = worker_ini


# worker abort hook
def worker_abort(worker):
    pass
worker_abort_hook = worker_abort


# before a new master process forked hook
def before_exec(server):
    pass
before_exec_hook = before_exec


# before handle a request
def before_handle_req(worker, req):
    pass
before_handle_req_hook = before_handle_req


# after handle req
def after_handle_req(worker, req, environ, resp):
    pass
after_handle_req_hook = after_handle_req


# child process ended hook
def after_child_exit(server, worker):
    pass
after_child_exit_hook = after_child_exit


# after worker exit
def after_worker_exit(server, worker):
    pass
after_worker_exit_hook = after_worker_exit


# number of the workers changed
def after_workernum_changed(server, new_value, old_value):
    pass
after_workernum_changed_hook = after_workernum_changed


# when exit server
def when_exit_server(server):
    pass
when_exit_server_hook = when_exit_server

