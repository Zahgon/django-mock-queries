from unittest.mock import patch, Mock

from model_bakery import baker

from .constants import *

SkipField = locate('rest_framework.fields.SkipField')


class SerializerAssert:
    _obj = None
    _serializer = None
    _return_fields = []
    _mock_fields = []
    _expected_values = {}

    def __init__(self, cls):
        self._cls = cls

    def _get_obj(self):
        pass

    def _get_attr(self, serializer, field):
        pass

    def _get_values_patchers(self, serializer):
        pass

    def _test_expected_fields(self, data, values):
        pass

    def _validate_args(self):
        pass

    @property
    def serializer(self):
        pass

    def instance(self, obj):
        pass

    def returns(self, *fields):
        pass

    def mocks(self, *fields):
        pass

    def values(self, **attrs):
        pass

    def run(self):
        pass


def assert_serializer(cls):
    pass
