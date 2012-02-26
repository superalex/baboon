import os
import pyinotify

from errors.baboon_exception import BaboonException
from config import config


class EventHandler(pyinotify.ProcessEvent):

    def __init__(self, service):
        """ @param service: the service in order to call some baboon util
        methods.
        """
        super(EventHandler, self).__init__()
        self.service = service

    def process_IN_CREATE(self, event):
        """ Triggered when a file is created in the watched project.
        @param event: the event provided by pyinotify.ProcessEvent.
        """
        print "File created : %s" % event.pathname

    def process_IN_MODIFY(self, event):
        """ Triggered when a file is modified in the watched project.
        @param event: the event provided by pyinotify.ProcessEvent.
        @raise BaboonException: if cannot retrieve the relative project path
        """
        print "File modified : %s" % event.pathname

        filename = os.path.basename(event.pathname)

        old_file_path = "%s%s%s" % (config.metadir_watched, os.sep, filename)
        new_file_path = "%s%s%s" % (config.path, os.sep, filename)

        rel_path = None
        try:
            rel_path = new_file_path.split(config.path)[1]
        except:
            err = 'Cannot retrieve the relative project path'
            raise BaboonException(err)

        patch = self.service.make_patch(old_file_path, new_file_path)
        self.service.broadcast(rel_path, patch)


class Monitor(object):
    def __init__(self, service):
        """ Watches file change events (creation, modification) in the
        watched project.
        @param service: Forwards the service to the L{EventHandler} class
        """
        self.service = service

        vm = pyinotify.WatchManager()
        mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE

        handler = EventHandler(service)

        self.monitor = pyinotify.ThreadedNotifier(vm, handler)
        self.monitor.coalesce_events()
        vm.add_watch(config.path, mask, rec=True)

    def watch(self):
        """ Starts to watch the watched project
        """
        self.monitor.start()