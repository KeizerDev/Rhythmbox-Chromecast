import errno
import os


def resolve_path(path):
    return os.path.join(os.path.dirname(__file__), path)


def log(message, args):
    # when debugging incomment the following line
    # sys.stdout.write("log %s:[%s]\n" % (message, args))
    return



def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e
