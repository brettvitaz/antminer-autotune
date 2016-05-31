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


def merge_dicts(*dict_args):
    """Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts."""
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class ListTraverse:
    def __init__(self, values, cur_value=None, min_value=None, max_value=None):
        self.values = values
        self.min_index = self.values.index(min_value) if min_value else 0
        self.max_index = self.values.index(max_value) if max_value else len(self.values) - 1
        self.index = self.values.index(cur_value) if cur_value else 0

    @property
    def current(self):
        return self.values[self.index]

    @current.setter
    def current(self, value):
        self.index = self.values.index(value)

    def _next(self, cur_value=None, step=1):
        if cur_value:
            self.current = cur_value
        if self.min_index > self.index + step:
            self.index = self.min_index
        elif self.max_index < self.index + step:
            self.index = self.max_index
        else:
            self.index += step

        return self.values[self.index]

    def next(self, cur_value=None, step=1):
        return self._next(cur_value, abs(step))

    def prev(self, cur_value=None, step=1):
        return self._next(cur_value, -abs(step))

    def is_valid(self, value):
        return bool(self.values.count(value) and self.min_index <= self.values.index(value) <= self.max_index)
