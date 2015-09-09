from __future__ import division
import warnings
from datetime import datetime
from dateutil.parser import parse
import importlib
import pytz


class PillowtopConfigurationException(Exception):
    pass


def import_settings():
    try:
        from django.conf import settings
    except Exception, ex:
        # if we are not in a django context, then import local pillowsettings
        print "django import"
        print ex
        import pillowsettings as settings
    return settings


def import_pillows(instantiate=True):
    warnings.warn('pillowtop.utils.import_pillows deprecated, '
                  'please use pillowtop.get_all_pillows instead.',
                  DeprecationWarning)
    return get_all_pillows(instantiate=instantiate)


def import_pillow_string(full_class_str, instantiate=True):
    mod_path, pillow_class_name = full_class_str.rsplit('.', 1)
    try:
        mod = importlib.import_module(mod_path)
        pillowtop_class = getattr(mod, pillow_class_name)
        return pillowtop_class() if instantiate else pillowtop_class
    except (AttributeError, ImportError):
        raise ValueError("Could not find pillowtop class '%s'" % full_class_str)

def get_all_pillows(instantiate=True):
    settings = import_settings()

    pillowtops = []
    if hasattr(settings, 'PILLOWTOPS'):
        for k, v in settings.PILLOWTOPS.items():
            for full_str in v:
                pillowtop_class = import_pillow_string(full_str, instantiate=instantiate)
                pillowtops.append(pillowtop_class)

    return pillowtops


def get_pillow_by_name(pillow_class_name):
    settings = import_settings()
    if hasattr(settings, 'PILLOWTOPS'):
        for k, v in settings.PILLOWTOPS.items():
            for full_str in v:
                if pillow_class_name in full_str:
                    return import_pillow_string(full_str)


def force_seq_int(seq):
    if seq is None:
        return None
    elif isinstance(seq, basestring):
        return int(seq.split('-')[0])
    else:
        assert isinstance(seq, int)
        return seq


def get_all_pillows_json():
    pillows = get_all_pillows()
    return [get_pillow_json(pillow) for pillow in pillows]


def get_pillow_json(pillow_or_name):
    if isinstance(pillow_or_name, basestring):
        pillow = get_pillow_by_name(pillow_or_name)
    else:
        pillow = pillow_or_name
    checkpoint = pillow.get_checkpoint()
    timestamp = checkpoint.get('timestamp')
    if timestamp:
        time_since_last = datetime.now(tz=pytz.UTC) - parse(timestamp)
        hours_since_last = time_since_last.total_seconds() // 3600

        try:
            # remove microsecond portion
            time_since_last = str(time_since_last)
            time_since_last = time_since_last[0:time_since_last.index('.')]
        except ValueError:
            pass
    else:
        time_since_last = ''
        hours_since_last = None
    return {
        'name': pillow.__class__.__name__,
        'seq': force_seq_int(checkpoint.get('seq')),
        'old_seq': force_seq_int(checkpoint.get('old_seq')) or 0,
        'db_seq': force_seq_int(pillow.get_db_seq()),
        'time_since_last': time_since_last,
        'hours_since_last': hours_since_last
    }
