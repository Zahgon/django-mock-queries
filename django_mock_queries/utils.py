from datetime import datetime, date
from django.core.exceptions import FieldError
from django.db.models import F, Value, Case
from django.db.models.functions import Coalesce
from unittest.mock import Mock

from .comparisons import *
from .constants import *
from .exceptions import *

import django_mock_queries.query


def merge(first, second):
    pass


def intersect(first, second):
    pass


def get_field_mapping(field):
    pass


def find_field_names_from_meta(meta, annotated=None, **kwargs):
    pass


def find_field_names_from_obj(obj, **kwargs):
    pass


def find_field_names(obj, **kwargs):
    pass


def validate_field(field_name, model_fields, for_update=False):
    pass


def get_field_value(obj, field_name, default=None):
    pass


def get_attribute(obj, attr, default=None):
    pass


def is_match(first, second, comparison=None):
    pass


def extract(obj, comparison):
    pass


def convert_to_pks(query):
    pass


def is_match_in_children(comparison, first, second):
    pass


def is_disqualified(obj, attrs, negated):
    pass


def matches(*source, **attrs):
    pass


def validate_mock_set(mock_set, for_update=False, **fields):
    pass


def validate_date_or_datetime(value, comparison):
    pass


def is_list_like_iter(obj):
    pass


def is_like_date_or_datetime(obj):
    pass


def flatten_list(source):
    pass


def truncate(obj, kind):
    pass


def hash_dict(obj, *fields):
    pass


def filter_results(source, query):
    pass


def _filter_single_q(source, q_obj, negated):
    pass


def get_nested_attr(obj, attr_path, default=None):
    pass
