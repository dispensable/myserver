# _*_coding:utf_8 _*_

from schema import Schema, Use, And, Or, Optional, SchemaUnexpectedTypeError, SchemaError
import os.path
import inspect
import pwd


def validate_hostport(hostport):
    if hostport is None:
        return None
    elements = hostport.split(":")
    if len(elements) == 2:
        return (elements[0], int(elements[1]))
    else:
        raise SchemaError('Not a host port string.')


def validate_class(user_class):
    if inspect.isfunction(user_class) or inspect.ismethod(user_class):
        val = user_class()
    if inspect.isclass(val):
        return val
    raise SchemaUnexpectedTypeError('Expect a class but not')


def validate_user(userid):
    if userid is None:
        return os.geteuid()
    if isinstance(userid, int):
        return userid
    elif userid.isdigit():
        return int(userid)
    else:
        try:
            return pwd.getpwnam(userid).pw_uid
        except KeyError:
            raise SchemaError('userid invaild')


def validate_func(function):
    if inspect.isfunction(function):
        return function
    raise SchemaUnexpectedTypeError('expect a function but get {}'.format(function))

schema = Schema(
    {
        'app': str,
        'module': str,
        'access_logfile': Or(None, str),
        'access_logformat': str,
        'backlog': And(Use(int), lambda backlog: 5 <= backlog <= 65535),
        'bind': [str],
        'ca_certs': Or(None, Use(open)),
        'capture_output': bool,
        'cert_reqs': And(Use(int), lambda n: n >= 0),
        'certfile': Or(None, Use(open)),
        'chdir': os.path.exists,
        'check_config': bool,
        'ciphers': str,
        'config': Or(None, Use(open)),
        'daemon': bool,
        'do_handshake_on_connect': bool,
        'enable_stdio_inheritance': bool,
        'env': [str],
        'forwarded_allow_ips': str,
        'graceful_timeout': And(Use(int), lambda time: time >= 0),
        'group': And(Use(int), lambda group: group >= 0),
        'help': bool,
        'initgroups': bool,
        'keep_alive': And(Use(int), lambda keep: keep >= 0),
        'keyfile': Or(None, Use(open)),
        'limit_request_field_size': And(Use(int), lambda size: size > 0),
        'limit_request_fields': And(Use(int), lambda fields: fields > 0),
        'limit_request_line': And(Use(int), lambda lines: lines > 0),
        'log_config': Or(None, Use(open)),
        'log_file': Or(None, str),
        'log_level': str,
        'log_syslog': bool,
        'log_syslog_facility': str,
        'log_syslog_prefix': Or(None, str),
        'log_syslog_to': str,
        'logger_class': str,
        'max_requests': And(Use(int), lambda n: n >= 0),
        'max_requests_jitter': And(Use(int), lambda n: n >= 0),
        'name': Or(None, str),
        'no_sendfile': bool,
        'paster': Or(None, str),
        'pid': Or(None, str),
        'preload': bool,
        'proxy_allow_from': [str],
        'proxy_protocol': bool,
        'pythonpath': Or(None, os.path.exists),
        'reload': bool,
        'reload_engine': str,
        'spew': bool,
        'ssl': bool,
        'ssl_version': And(Use(int), lambda sslv: sslv >= 1),
        'statsd_host': Or(None, Use(validate_hostport)),
        'statsd_prefix': str,
        'suppress_ragged_eofs': bool,
        'threads': And(Use(int), lambda n: n >= 0),
        'timeout': And(Use(int), lambda n: n >= 0),
        'umask': And(Use(int), lambda n: n >= 0),
        'user': Use(validate_user),
        'version': bool,
        'worker_class': str,
        'worker_connections': And(Use(int), lambda n: n >= 0),
        'worker_tmp_dir': Or(None, os.path.exists),
        'workers': And(Use(int), lambda n: n > 0),
        Optional('is_ssl'): bool,
        Optional('after_child_exit_hook'): Use(validate_func),
        Optional('on_staring'): Use(validate_func),
        Optional('before_fork_worker'): Use(validate_func),
        Optional('worker_ini'): Use(validate_func),
        Optional('before_exec_hook'): Use(validate_func),
        Optional('before_handle_req'): Use(validate_func),
        Optional('when_booted'): Use(validate_func),
        Optional('after_handle_req_hook'): Use(validate_func),
        Optional('after_worker_quit'): Use(validate_func),
        Optional('on_reload_hook'): Use(validate_func),
        Optional('after_worker_fork'): Use(validate_func),
        Optional('worker_abort'): Use(validate_func),
        Optional('after_worker_forked'): Use(validate_func),
        Optional('after_handle_req'): Use(validate_func),
        Optional('before_forke_worker'): Use(validate_func),
        Optional('after_worker_init'): Use(validate_func),
        Optional('after_workernum_changed_hook'):Use(validate_func),
        Optional('on_starting_hook'): Use(validate_func),
        Optional('worker_abort_hook'): Use(validate_func),
        Optional('when_exit_server_hook'): Use(validate_func),
        Optional('default_proc_name'): str,
        Optional('after_worker_inited'): Use(validate_func),
        Optional('after_child_exit'): Use(validate_func),
        Optional('before_handle_req_hook'): Use(validate_func),
        Optional('after_worker_exit'): Use(validate_func),
        Optional('on_booted_hook'): Use(validate_func),
        Optional('when_exit_server'): Use(validate_func),
        Optional('tmp_upload_dir'): Or(None, os.path.exists),
        Optional('after_worker_exit_hook'): Use(validate_func),
        Optional('secure_scheme_headers'): dict,
        Optional('after_workernum_changed'): Use(validate_func),
        Optional('before_exec'): Use(validate_func),
        Optional('on_reload'): Use(validate_func),
        Optional('nworkers_changed'): Use(validate_func),
        Optional('before_worker_init'): Use(validate_func)
    },
    ignore_extra_keys=True
)

