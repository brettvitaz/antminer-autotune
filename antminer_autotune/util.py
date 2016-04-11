import errno

import os


def makedir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def fix_json_format(bad_json):
    return bad_json.replace('}{', '},{').strip(' \0')
