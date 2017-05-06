.. MyServer server configuration

服务器选项配置
================

从命令行配置
--------------

使用命令行-h选项可查看所有可配置项：

.. code-block:: shell

   $ myserver -h


从配置文件配置
-----------------

使用以下命令指定配置文件

.. code-block:: shell

   $ myserver -c <configfile>

配置文件为普通的python文件，你可以在`/myserver/config/default_conf.py`查看所有可配置项。
配置文件应该是一个python模块。具体可配置选项如下：


# default config in file

access_logfile
^^^^^^^^^^^^^^

    默认值：None

    可选值：文件绝对路径

    说明：该文件用来写入所有处理的连接记录，记录格式如下

    示例：access_logfile = '/tmp/log'

access_logformat
^^^^^^^^^^^^^^^^

    默认值：'%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

    可选值：`Apache log format <http://httpd.apache.org/docs/current/mod/mod_log_config.html>`_

    说明：决定接入连接的log格式

backlog
^^^^^^^

    默认值：2048

    可选值：整数，根据使用的内核backlog队列长度决定最大数值

    说明：backlog是未决连接的数量，客户端可能在服务器调用accept()之前调用connect()，
    服务器忙于处理其他客户端的时候，将会产生一个悬而未决的连接。backlog就是用来指定需要保存的连接信息的队列的长度。

bind
^^^^

    默认值：'127.0.0.1:8000'

    可选值：ipv4地址和相关网络端口

    说明：服务器绑定的本地地址

ssl
^^^

    默认值： False

    可选值： True/False

    说明： 是否启用ssl

ca_certs
^^^^^^^^

    默认值： None

    可选值： 证书路径

    说明： CA证书所在的系统路径

capture_output
^^^^^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否捕获输出

    示例:

.. code-block:: python

   capture_output = False

cert_reqs
^^^^^^^^^

    默认值: 0

    可选值: 0/1

    说明: 是否需要客户端证书

    示例:

.. code-block:: python

   cert_reqs = 0

certfile
^^^^^^^^

    默认值: None

    可选值: 文件路径

    说明: ssl证书文件

    示例:

.. code-block:: python

   certfile = '/path/to/ca'

chdir
^^^^^

    默认值: '/Users/apple'

    可选值: app 所在路径

    说明: app所在路径

    示例:

.. code-block:: python

   chdir = '/Users/apple'

check_config
^^^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 检查配置文件是否错误

    示例:

.. code-block:: python

   check_config = False

ciphers
^^^^^^^

    默认值: 'TLSv1'

    可选值: ssl版本 [#]_

.. [#] 见 `SSL and TLS version<https://wiki.openssl.org/index.php/SSL_and_TLS_Protocols>`_

    说明: `TSL<https://tools.ietf.org/html/rfc5246>`_

    示例:

.. code-block:: python

   ciphers = 'TLSv1'

config
^^^^^^

    默认值: None

    可选值: 配置文件路径

    说明: 讲从本路径加载配置文件

    示例:

.. code-block:: python

   config = '/your/conf/file.py'

daemon
^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否将本进程设置为守护进程

    示例:

.. code-block:: python

   daemon = False

do_handshake_on_connect
^^^^^^^^^^^^^^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否在ssl连接时握手 [#]_

.. [#] 参见`ssl module<https://docs.python.org/3/library/ssl.html#ssl.wrap_socket>`_

    示例:

.. code-block:: python

   do_handshake_on_connect = False

enable_stdio_inheritance
^^^^^^^^^^^^^^^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否启用标准输出继承，启用后子进程将继承父进程的stdio

    示例:

.. code-block:: python

   enable_stdio_inheritance = False

env
^^^

    默认值: []

    可选值: key=value

    说明: 输入的键值对将覆盖相关的环境变量

    示例:

.. code-block:: python

   env = []

forwarded_allow_ips
^^^^^^^^^^^^^^^^^^^

    默认值: '127.0.0.1'

    可选值: ipv4地址

    说明: 允许转发ip

    示例:

.. code-block:: python

   forwarded_allow_ips = '127.0.0.1'

graceful_timeout
^^^^^^^^^^^^^^^^

    默认值: 30

    可选值: int > 0 （s）

    说明: 使用term信号退出时，清理进程的定时器时间，若超时后仍未结束，将使用kill杀死进程，单位为秒

    示例:

.. code-block:: python

   graceful_timeout = 30

group
^^^^^

    默认值: 20

    可选值: 进程组id

    说明: 设置后进程组id为该id

    示例:

.. code-block:: python

   group = 20

help
^^^^

    默认值: False

    可选值: True/False

    说明: 是否显示帮助信息，使用-h亦可

    示例:

.. code-block:: python

   help = False

initgroups
^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 如果为真，将设置所有的worker进程组的ACL

    示例:

.. code-block:: python

   initgroups = False

keep_alive
^^^^^^^^^^

    默认值: 2

    可选值: int

    说明: 保持连接的等待秒数，超时后讲断开连接

    示例:

.. code-block:: python

   keep_alive = 2

keyfile
^^^^^^^

    默认值: None

    可选值: ssl key 文件

    说明: ssl key file

    示例:

.. code-block:: python

   keyfile = '/your/key/file'

limit_request_field_size
^^^^^^^^^^^^^^^^^^^^^^^^

    默认值: 8190

    可选值: int > 0

    说明: 请求体的字节数

    示例:

.. code-block:: python

   limit_request_field_size = 8190

limit_request_fields
^^^^^^^^^^^^^^^^^^^^

    默认值: 100

    可选值: int > 0

    说明: 请求体的headers数量限制

    示例:

.. code-block:: python

   limit_request_fields = 100

limit_request_line
^^^^^^^^^^^^^^^^^^

    默认值: 4094

    可选值: int > 0

    说明: 请求体的最大请求行数（用字节计算）

    示例:

.. code-block:: python

   limit_request_line = 4094

log_config
^^^^^^^^^^

    默认值: None

    可选值: log 配置文件

    说明: log 配置文件

    示例:

.. code-block:: python

   log_config = None

log_file
^^^^^^^^

    默认值: sys.stderr

    可选值: log file

    说明: log的输出文件

    示例:

.. code-block:: python

   log_file = sys.stderr

log_level
^^^^^^^^^

    默认值: 'info'

    可选值: critical/error/warning/info/debug

    说明: log 级别

    示例:

.. code-block:: python

   log_level = 'info'

log_syslog
^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否将log输出到syslog

    示例:

.. code-block:: python

   log_syslog = False

log_syslog_facility
^^^^^^^^^^^^^^^^^^^

    默认值: 'user'

    可选值: `RFC3164<https://tools.ietf.org/html/rfc3164#section-4.1.1>`_

    说明: syslog facility

    示例:

.. code-block:: python

   log_syslog_facility = 'user'

log_syslog_prefix
^^^^^^^^^^^^^^^^^

    默认值: None

    可选值: 字符串

    说明: syslog 前缀

    示例:

.. code-block:: python

   log_syslog_prefix = None

log_syslog_to
^^^^^^^^^^^^^

    默认值: 'unix:///var/run/syslog'

    可选值: unix域套接字

    说明: syslog接收地址

    示例:

.. code-block:: python

   log_syslog_to = 'unix:///var/run/syslog'

logger_class
^^^^^^^^^^^^

    默认值: 'logger.Logger'

    可选值: logger类

    说明: 使用的logger类

    示例:

.. code-block:: python

   logger_class = 'logger.Logger'

max_requests
^^^^^^^^^^^^

    默认值: 0

    可选值: int

    说明: worker处理请求的总数限制（超过后将重启worker）

    示例:

.. code-block:: python

   max_requests = 0

max_requests_jitter
^^^^^^^^^^^^^^^^^^^

    默认值: 0

    可选值: int

    说明: 单个worker能接收的请求总数的抖动值

    示例:

.. code-block:: python

   max_requests_jitter = 0

name
^^^^

    默认值: None

    可选值: 字符串

    说明: 进程名称

    示例:

.. code-block:: python

   name = None

no_sendfile
^^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明: 禁用`sendfile<https://www.ibm.com/developerworks/cn/linux/l-cn-zerocopy2/>`_ 系统调用

    示例:

.. code-block:: python

   no_sendfile = False

paster
^^^^^^

    默认值: None

    可选值:

    说明:

    示例:

.. code-block:: python

   paster = None

pid
^^^^

    默认值: None

    可选值: 字符串

    说明: pid file的名称

    示例:

.. code-block:: python

   pid = None

preload
^^^^^^^

    默认值: True

    可选值: True/False

    说明: 是否需要提前预加载应用

    示例:

.. code-block:: python

   preload = True

proxy_allow_from
^^^^^^^^^^^^^^^^

    默认值: '127.0.0.1'

    可选值: ipv4地址

    说明: 允许的转发地址

    示例:

.. code-block:: python

   proxy_allow_from = '127.0.0.1'

proxy_protocol
^^^^^^^^^^^^^^

    默认值: False

    可选值: True/False

    说明:

    示例:

.. code-block:: python

   proxy_protocol = False

pythonpath
^^^^^^^^^^

    默认值: None

    可选值: 路径

    说明: Python解释器路径

    示例:

.. code-block:: python

   pythonpath = None

reload
^^^^^^

    默认值: True

    可选值: True/False

    说明: 文件变化时是否自动重启worker

    示例:

.. code-block:: python

   reload = True

is_ssl
^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否启用SSL

    示例:

.. code-block:: python

   is_ssl = False

reload_engine
^^^^^^^^^^^^^

    默认值: 'auto'

    可选值: auto/inotify/poll

    说明: auto 自动根据平台选择重新载入机制（inotify > poll)

    示例:

.. code-block:: python

   reload_engine = 'auto'

spew
^^^^

    默认值: False

    可选值:

    说明:

    示例:

.. code-block:: python

   spew = False

ssl_version
^^^^^^^^^^^

    默认值: 3

    可选值: see `TSL AND SSL VERSION<https://wiki.openssl.org/index.php/SSL_and_TLS_Protocols>`_

    说明: SSL 版本

    示例:

.. code-block:: python

   ssl_version = 3

statsd_host
^^^^^^^^^^^

    默认值: None

    可选值:

    说明:

    示例:

.. code-block:: python

   statsd_host = None

statsd_prefix
^^^^^^^^^^^^^

    默认值: ""

    可选值:

    说明:

    示例:

.. code-block:: python

   statsd_prefix = ""

suppress_ragged_eofs
^^^^^^^^^^^^^^^^^^^^

    默认值: False

    可选值:

    说明:

    示例:

.. code-block:: python

   suppress_ragged_eofs = False

threads
^^^^^^^

    默认值: 1

    可选值: int

    说明: 线程数量

    示例:

.. code-block:: python

   threads = 1

timeout
^^^^^^^

    默认值: 30

    可选值: int

    说明: 超时后worker将被杀死

    示例:

.. code-block:: python

   timeout = 30

umask
^^^^^

    默认值: 0

    可选值: int

    说明: 权限掩码

    示例:

.. code-block:: python

   umask = 0

user
^^^^

    默认值: 501

    可选值: int

    说明: worker进程将以该user运行

    示例:

.. code-block:: python

   user = 501

version
^^^^^^^

    默认值: False

    可选值: True/False

    说明: 是否显示版本号

    示例:

.. code-block:: python

   version = False

worker_class
^^^^^^^^^^^^

    默认值: 'sync'

    可选值: sync

    说明: worker类型

    示例:

.. code-block:: python

   worker_class = 'sync'

worker_connections
^^^^^^^^^^^^^^^^^^

    默认值: 1000

    可选值: int

    说明: 最大并发用户数

    示例:

.. code-block:: python

   worker_connections = 1000

worker_tmp_dir
^^^^^^^^^^^^^^

    默认值: None

    可选值: tmp url

    说明: worker创建临时文件的目录

    示例:

.. code-block:: python

   worker_tmp_dir = None

workers
^^^^^^^

    默认值: 4

    可选值: int >= 1

    说明: worker数量

    示例:

.. code-block:: python

   workers = 4

tmp_upload_dir
^^^^^^^^^^^^^^

    默认值: None

    可选值: tmp dir

    说明: 上传文件暂存目录

    示例:

.. code-block:: python

   tmp_upload_dir = None




secure_scheme_headers

    |默认值：{
    |    "X-FORWARDED-PROTOCOL": "ssl",
    |"X-FORWARDED-PROTO": "https",
    |"X-FORWARDED-SSL": "on"
    |}

    可选值：设置该字典的相关header

    说明：转发代理用来提示该链接是ssl连接的代理头部

    示例：

.. code-block:: python

    secure_scheme_headers = {
        "X-FORWARDED-PROTOCOL": "ssl",
        "X-FORWARDED-PROTO": "https",
        "X-FORWARDED-SSL": "on"
    }


default_proc_name
^^^^^^^^^^^^^^^^^

    默认值： 'myserver'

    可选值： 字符串

    说明： 进程名

    示例：
.. code-block:: python

   default_proc_name = 'your proccess name'

服务器钩子
^^^^^^^^^
服务器钩子用来在特定时期触发，可以自定义钩子的内容，传递的参数已经在示例函数中

.. code-block:: python

    # worker count changed hook
    def at_worker_count_changed(new, old):
         pass
    nworkers_changed = at_worker_count_changed

    # 服务器启动时的钩子
    def on_starting(server):
        pass
    on_starting_hook = on_starting


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

