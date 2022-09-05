import json
import os
import functools

import pymongo
import threading


def rate_add(*a):
    result = 0
    for x in a:
        result = result + x - result * x
    return result


def rate_and(*a):
    result = 1
    for x in a:
        result = result * x
    return result


def cache_for_threading(f):
    lock = threading.Lock()
    f_ = functools.lru_cache()(f)

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with lock:
            return f_(*args, **kwargs)

    return wrapper


@cache_for_threading
def get_client():
    mongo_uri = os.getenv('MONGO_URI')
    client = pymongo.MongoClient(mongo_uri)
    return client


def get_database(database='pjsekai'):
    return get_client()[database]


def get_collection(database='pjsekai'):
    return get_database(database)['accounts']


class FloatEncoder(json.JSONEncoder):

    def iterencode(self, o, _one_shot=False):
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = json.encoder.encode_basestring_ascii
        else:
            _encoder = json.encoder.encode_basestring

        def floatstr(o,
                     allow_nan=self.allow_nan,
                     _repr=float.__repr__,
                     _inf=json.encoder.INFINITY,
                     _neginf=-json.encoder.INFINITY):

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(float("%g" % o))

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        _iterencode = json.encoder._make_iterencode(
            markers, self.default, _encoder, self.indent, floatstr,
            self.key_separator, self.item_separator, self.sort_keys,
            self.skipkeys, _one_shot)

        return _iterencode(o, 0)
