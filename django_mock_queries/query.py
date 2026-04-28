import datetime
import random
from collections import OrderedDict, defaultdict, namedtuple
from unittest.mock import Mock, MagicMock, PropertyMock

from .constants import *
from .exceptions import *
from .utils import (
    matches, get_attribute, validate_mock_set, is_list_like_iter, flatten_list, truncate,
    hash_dict, filter_results, get_nested_attr
)


class MockSetMeta(type):
    def __call__(cls, *initial_items, **kwargs):
        pass


class MockSet(MagicMock, metaclass=MockSetMeta):
    EVENT_ADDED = 'added'
    EVENT_UPDATED = 'updated'
    EVENT_SAVED = 'saved'
    EVENT_DELETED = 'deleted'
    SUPPORTED_EVENTS = [EVENT_ADDED, EVENT_UPDATED, EVENT_SAVED, EVENT_DELETED]
    RETURN_SELF_METHODS = [
        'all',
        'only',
        'defer',
        'using',
        'select_related',
        'prefetch_related',
        'select_for_update',
        'iterator'
    ]

    def __init__(self, *initial_items, **kwargs):
        pass

    def _return_self(self, *_, **__):
        pass

    def _mockset_class(self):
        pass

    def count(self):
        pass

    def fire(self, obj, *events):
        pass

    def on(self, event, handler):
        pass

    def _register_fields(self, obj):
        pass

    def add(self, *models):
        pass

    def filter(self, *args, **attrs):
        pass

    def exclude(self, *args, **attrs):
        pass

    def exists(self):
        pass

    def in_bulk(self, id_list=None, *, field_name='pk'):
        pass

    def annotate(self, **kwargs):
        pass

    def aggregate(self, *args, **kwargs):
        pass

    def order_by(self, *fields):
        pass

    def distinct(self, *fields):
        pass

    def set(self, objs, **attrs):
        pass

    def _raise_does_not_exist(self):
        pass

    def _get_order_fields(self, fields, field_name):
        pass

    def _earliest_or_latest(self, *fields, **field_kwargs):
        """
        Mimic Django's behavior
        https://github.com/django/django/blob/746caf3ef821dbf7588797cb2600fa81b9df9d1d/django/db/models/query.py#L560
        """
        pass

    def earliest(self, *fields, **field_kwargs):
        pass

    def latest(self, *fields, **field_kwargs):
        pass

    def first(self):
        pass

    def last(self):
        pass

    def create(self, **attrs):
        pass

    def update(self, **attrs):
        pass

    def _delete_recursive(self, *items_to_remove, **attrs):
        pass

    def delete(self, **attrs):
        # Delete normally doesn't take **attrs - they're only needed for remove
        pass

    # The following 2 methods were kept for backwards compatibility and
    # should be removed in the future since they are covered by filter & delete
    def clear(self, **attrs):
        pass

    def remove(self, **attrs):
        pass

    def get(self, *args, **attrs):
        pass

    def get_or_create(self, defaults=None, **attrs):
        pass

    def update_or_create(self, defaults=None, **attrs):
        pass

    def _item_values(self, item, fields):
        pass

    def values(self, *fields):
        pass

    def _item_values_list(self, values_dict, fields, flat):
        pass

    def _values_row(self, values_dict, fields, **kwargs):
        pass

    def values_list(self, *fields, **kwargs):
        # Django doesn't complain about this:
        # https://github.com/django/django/blob/a4e6030904df63b3f10aa0729b86dc6942b0458e/django/db/models/query.py#L845
        # if len(fields) == 0:
        #     raise NotImplementedError('values_list() with no arguments is not implemented')

        pass

    def _date_values(self, field, kind, order, key_func):
        pass

    def dates(self, field, kind, order='ASC'):
        pass

    def datetimes(self, field, kind, order='ASC'):
        # TODO: Handle `tzinfo` parameter
        pass


class MockModel(dict):
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, item):
        pass

    def __setattr__(self, key, value):
        pass

    def __hash__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def get_fields(self):
        pass

    @property
    def _meta(self):
        pass

    def __repr__(self):
        pass


def create_model(*fields):
    pass


class MockOptions:
    def __init__(self, object_name, *field_names):
        pass

    @property
    def label(self):
        pass

    @property
    def label_lower(self):
        pass

    def load_fields(self, *field_names):
        pass


class MockField:
    def __init__(self, field):
        pass
