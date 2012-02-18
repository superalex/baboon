import os
import shutil
import errno
from config import config
from errors.baboon_exception import BaboonException


class Initializor(object):
    def __init__(self):
        self.metadir = os.path.join(config.path, config.metadir_name)

    def create_metadir(self):
        try:
            os.mkdir(self.metadir)
        except OSError, err:
            if err.errno in (errno.EEXIST, errno.ENOENT):
                raise BaboonException("Baboon error : %s - %s" %
                                      (err.strerror,
                                       os.path.abspath(self.metadir)))
            else:
                raise

    def create_config_file(self):
        """ This is git-like. Config files holds folders that must be watched
        by the mighty Baboon.
        """

        config_file_path = os.sep.join([self.metadir, 'config'])
        try:
            open(config_file_path, 'a').close()
        except OSError, err:
            if err.errno in (errno.EPERM):
                raise BaboonException("Baboon error : %s - %s" %
                                      (err.strerror,
                                       os.path.abspath(config_file_path)))
            else:
                raise

    def walk_and_copy(self):
        """ This methods walks down the folders and recursively copy any
        non-hidden folders and files to the metadir folder.
        """
        src = os.sep.join(self.metadir.split(os.sep)[:-1])
        dest = os.sep.join([self.metadir, 'watched'])
        try:
            shutil.copytree(src, dest, ignore=lambda adir, files:
                                [f for f in files if f.startswith('.')])

        except (shutil.Error, OSError), err:
            raise BaboonException("Baboon error: %s" % (err,))