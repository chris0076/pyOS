import os
import shutil
import imp
import glob
import argparse

from kernel.constants import BASEPATH

def abs_path(path):
    # returns external absolute path
    return os.path.abspath(os.path.join(BASEPATH, path.lstrip('/')))

def rel_path(path, base):
    # returns external relative path
    return os.path.relpath(path, base)

def irel_path(path):
    # returns internal relative path
    path = abs_path(path)
    b = os.path.relpath(path, BASEPATH)
    b = b.replace('../', '')
    if b in ('..', '.'):
        b = ''
    return b

def iabs_path(path):
    # returns internal absolute path
    a = os.path.commonprefix([BASEPATH, abs_path(path)])
    b = os.path.relpath(abs_path(path), BASEPATH)
    c = irel_path(path)
    return join_path('/', c)

def exists(path):
    return os.path.exists(abs_path(path))

def is_file(path):
    return os.path.isfile(abs_path(path))

def is_directory(path):
    return os.path.isdir(abs_path(path))

def move(src, dst):
    shutil.move(abs_path(src), abs_path(dst))

def copy(src, dst, recursive=False):
    if recursive:
        shutil.copytree(abs_path(src), abs_path(dst))
    else:
        shutil.copy2(abs_path(src), abs_path(dst))

def remove(path, recursive=False):
    if recursive:
        shutil.rmtree(abs_path(path))
    else:
        os.remove(abs_path(path))

def join_path(*args):
    return os.path.join(*args)

def get_size(path):
    return os.path.getsize(abs_path(path))

def list_dir(path):
    return sorted(x for x in os.listdir(abs_path(path)) if ".git" not in x and not x.endswith(".pyc"))

def list_glob(expression):
    return [iabs_path(x) for x in glob.glob(abs_path(expression))]

def list_all(path="/"):
    listing = []
    for x in list_dir(path):
        new = join_path(path, x)
        if is_directory(new):
            listing.extend(list_all(new))
        else:
            listing.append(new)
    return listing

def make_dir(path):
    return os.mkdir(abs_path(path))

def open_file(path, mode):
    return open(abs_path(path), mode)

def open_program(path):
    x = abs_path(path)
    try:
        try:
            program = imp.load_source('program', '%s.py' % (x, ))
        except IOError:
            program = imp.load_source('program', x)
    except IOError:
        program = False
    return program

def dir_name(path):
    return os.path.dirname(abs_path(path))

def base_name(path):
    return os.path.basename(abs_path(path))

def split(path):
    return dir_name(path), base_name(path)


class Parser(argparse.ArgumentParser):
    def __init__(self, program, name=None, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, prog=program, *args, **kwargs)
        if name is None:
            self.name = program
        else:
            self.name = name
        self.help = False

    def add_shell(self, shell):
        self.shell = shell

    def exit(self, *args, **kwargs):
        pass

    def print_usage(self, *args, **kwargs):
        try:
            self.shell.stderr.write(self.format_usage())
            self.help = True
        except AttributeError:
            pass

    def print_help(self, *args, **kwargs):
        try:
            self.shell.stdout.write(self.help_msg())
            self.help = True
        except AttributeError:
            pass

    def help_msg(self):
        return "%s\n\n%s" % (self.name, self.format_help())
