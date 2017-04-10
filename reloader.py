import sys
import re
import os
import threading
import time
import os.path


class Reloader(threading.Thread):
    def __init__(self, extra_files=None, callback=None, interval=1):
        super(Reloader, self).__init__()
        self.setDaemon(True)
        self.callback = callback

        self.file = set(self.get_filename())
        self.extra_files = extra_files
        self.interval = interval

    def get_files_or_dir(self):
        return self.file

    def add_extra(self, extra):
        raise NotImplementedError

    def get_filename(self):
        return [
            re.sub('py[co]$', 'py', module.__file__)
            for module in list(sys.modules.values())
            if hasattr(module, '__file__')
            ]

    def run(self):
        raise NotImplementedError


class FileReloader(Reloader):
    def __init__(self, extra_files=None, callback=None, interval=1):
        super(FileReloader, self).__init__(extra_files, callback, interval)
        self.lock = threading.RLock()

    def add_extra(self, extra):
        with self.lock:
            self.file.add(extra)

    def run(self):
        mtimes = {}
        while True:
            for filename in self.file:
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    continue
                old_time = mtimes.get(filename)
                if old_time is None:
                    mtimes[filename] = mtime
                    continue
                elif mtime > old_time:
                    if self.callback:
                        self.callback(filename)
            time.sleep(self.interval)

try:
    from inotify.adapters import Inotify
    import inotify.constants
    has_inotify = True
except ImportError:
    has_inotify = False


class InotifyReloader():
    def __init__(self, callback=None):
        raise ImportError('You must have the inotify module installed to use '
                          'the inotify reloader')

if has_inotify:
    class InotifyReloader(Reloader):

        event_mask = (inotify.constants.IN_CREATE | inotify.constants.IN_DELETE
                      | inotify.constants.IN_DELETE_SELF | inotify.constants.IN_MODIFY
                      | inotify.constants.IN_MOVE_SELF | inotify.constants.IN_MOVED_FROM
                      | inotify.constants.IN_MOVED_TO)

        def __init__(self, extra_files=None, callback=None):
            super(InotifyReloader, self).__init__(extra_files, callback)
            self.watcher = Inotify()

        def get_files_or_dir(self):
            dirs = set([os.path.dirname(path) for path in self.file])
            self.file = dirs

        def add_extra(self, extra):
            dirname = os.path.dirname(extra)

            if dirname in self.file:
                return

            self.watcher.add_watch(dirname, mask=self.event_mask)
            self.file.add(dirname)

        def run(self):
            for dirname in self.file:
                self.watcher.add_watch(dirname, mask=self.event_mask)

            for event in self.watcher.event_gen():
                if event is None:
                    continue
                filename = event[3]

                self.callback(filename)

auto_reloader = InotifyReloader if has_inotify else FileReloader

reloaders = {
    'auto': auto_reloader,
    'poll': FileReloader,
    'inotify': InotifyReloader
}