import os
import sys
import django
import weakref
from django.apps import apps
from django.db import connections
from django.db.backends.base import creation
from django.db.models import Model
from django.db.utils import ConnectionHandler, NotSupportedError
from functools import partial
from itertools import chain
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from types import MethodType

from .query import MockSet

# noinspection PyUnresolvedReferences
patch_object = patch.object


def monkey_patch_test_db(disabled_features=None):
    """ Replace the real database connection with a mock one.

    This is useful for running Django tests without the cost of setting up a
    test database.
    Any database queries will raise a clear error, and the test database
    creation and tear down are skipped.
    Tests that require the real database should be decorated with
    @skipIfDBFeature('is_mocked')
    :param disabled_features: a list of strings that should be marked as
        *False* on the connection features list. All others will default
        to True.
    """

    # noinspection PyUnusedLocal
    def create_mock_test_db(self, *args, **kwargs):
        pass

    # noinspection PyUnusedLocal
    def destroy_mock_test_db(self, *args, **kwargs):
        pass

    creation.BaseDatabaseCreation.create_test_db = create_mock_test_db
    creation.BaseDatabaseCreation.destroy_test_db = destroy_mock_test_db


def mock_django_setup(settings_module, disabled_features=None):
    """ Must be called *AT IMPORT TIME* to pretend that Django is set up.

    This is useful for running tests without using the Django test runner.
    This must be called before any Django models are imported, or they will
    complain. Call this from a module in the calling project at import time,
    then be sure to import that module at the start of all mock test modules.
    Another option is to call it from the test package's init file, so it runs
    before all the test modules are imported.
    :param settings_module: the module name of the Django settings file,
        like 'myapp.settings'
    :param disabled_features: a list of strings that should be marked as
        *False* on the connection features list. All others will default
        to True.
    """
    if apps.ready:
        # We're running in a real Django unit test, don't do anything.
        return

    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    django.setup()
    mock_django_connection(disabled_features)


def mock_django_connection(disabled_features=None):
    """ Overwrite the Django database configuration with a mocked version.

    This is a helper function that does the actual monkey patching.
    """
    db = connections.databases['default']
    db['PASSWORD'] = '****'
    db['USER'] = '**Database disabled for unit tests**'
    ConnectionHandler.__getitem__ = MagicMock(name='mock_connection')
    # noinspection PyUnresolvedReferences
    mock_connection = ConnectionHandler.__getitem__.return_value
    if disabled_features:
        for feature in disabled_features:
            setattr(mock_connection.features, feature, False)
    mock_ops = mock_connection.ops

    # noinspection PyUnusedLocal
    def compiler(queryset, using=None, connection=None, elide_empty=True, **kwargs):
        pass

    mock_ops.compiler.return_value.side_effect = compiler
    mock_ops.integer_field_range.return_value = (-sys.maxsize - 1, sys.maxsize)
    mock_ops.max_name_length.return_value = sys.maxsize

    Model.refresh_from_db = Mock()  # Make this into a noop.


class MockMap:
    def __init__(self, original):
        """ Wrap a mock mapping around the original one-to-many relation. """
        self.map = {}
        self.original = original

    def __set__(self, instance, value):
        """ Set a related object for an instance. """
        pass

    def __getattr__(self, name):
        """ Delegate all other calls to the original. """
        pass


class MockOneToManyMap(MockMap):
    def __get__(self, instance, owner):
        """ Look in the map to see if there is a related set.

        If not, create a new set.
        """
        pass


class MockOneToOneMap(MockMap):
    def __get__(self, instance, owner):
        """ Look in the map to see if there is a related object.

        If not (the default) raise the expected exception.
        """
        pass


def find_all_models(models):
    """ Yield all models and their parents. """
    for model in models:
        yield model
        # noinspection PyProtectedMember
        for parent in model._meta.parents.keys():
            yield from find_all_models((parent,))


def _patch_save(model, name):
    return patch_object(
        model,
        'save',
        new_callable=partial(Mock, name=name + '.save')
    )


def _patch_objects(model, name):
    return patch_object(
        model, 'objects',
        new_callable=partial(MockSet, mock_name=name + '.objects', model=model)
    )


def _patch_relation(model, name, related_object):
    relation = getattr(model, name)

    if related_object.one_to_one:
        new_callable = partial(MockOneToOneMap, relation)
    else:
        new_callable = partial(MockOneToManyMap, relation)

    return patch_object(model, name, new_callable=new_callable)


# noinspection PyProtectedMember
def mocked_relations(*models):
    """ Mock all related field managers to make pure unit tests possible.

    The resulting patcher can be used just like one from the mock module:
    As a test method decorator, a test class decorator, a context manager,
    or by just calling start() and stop().

    @mocked_relations(Dataset):
    def test_dataset(self):
        dataset = Dataset()
        check = dataset.content_checks.create()  # returns a ContentCheck object
    """
    patchers = []

    for model in find_all_models(models):
        if isinstance(model.save, Mock):
            # already mocked, so skip it
            continue

        model_name = model._meta.object_name
        patchers.append(_patch_save(model, model_name))

        if hasattr(model, 'objects'):
            patchers.append(_patch_objects(model, model_name))

        for related_object in chain(model._meta.related_objects,
                                    model._meta.many_to_many):
            name = related_object.name

            if name not in model.__dict__ and related_object.one_to_many:
                name += '_set'

            if name in model.__dict__:
                # Only mock direct relations, not inherited ones.
                if getattr(model, name, None):
                    patchers.append(_patch_relation(
                        model, name, related_object
                    ))

    return PatcherChain(patchers, pass_mocks=False)


class PatcherChain:
    """ Chain a list of mock patchers into one.

    The resulting patcher can be used just like one from the mock module:
    As a test method decorator, a test class decorator, a context manager,
    or by just calling start() and stop().
    """

    def __init__(self, patchers, pass_mocks=True):
        """ Initialize a patcher.

        :param patchers: a list of patchers that should all be applied
        :param pass_mocks: True if any mock objects created by the patchers
        should be passed to any decorated test methods.
        """
        self.patchers = patchers
        self.pass_mocks = pass_mocks

    def __call__(self, func):
        pass

    def decorate_class(self, cls):
        pass

    def decorate_callable(self, target):
        """ Called as a decorator. """
        pass

    def __enter__(self):
        """ Starting a context manager.

        All the patched objects are passed as a list to the with statement.
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Ending a context manager. """
        pass

    def start(self):
        pass

    def stop(self):
        pass


class Mocker:
    """
    A decorator that patches multiple class methods with a magic mock instance that does nothing.
    """

    def __init__(self, cls, *methods, **kwargs):
        self.cls = cls
        self.methods = methods

        self.inst_mocks = {}
        self.inst_patchers = {}
        self.inst_original = {}

    def __enter__(self):
        pass

    def __call__(self, func):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _key(self, method, obj=None):
        pass

    def _method_obj(self, name, obj, *sources):
        pass

    def method(self, name, obj=None):
        pass

    def original_method(self, name, obj=None):
        pass

    def _get_source_method(self, obj, method):
        pass

    def _patch_method(self, method_name, source_obj, source_method):
        pass

    def _patch_object_methods(self, obj, *methods, **kwargs):
        pass


class ModelMocker(Mocker):
    """
    A decorator that patches django base model's db read/write methods and wires them to a MockSet.
    """

    default_methods = ['objects', '_do_update', 'delete']

    if django.VERSION[0] >= 3:
        default_methods += ['_base_manager._insert', ]
    else:
        default_methods += ['_meta.base_manager._insert', ]

    default_methods = tuple(default_methods)

    def __init__(self, cls, *methods, **kwargs):
        pass

    def __enter__(self):
        pass

    def _obj_pk(self, obj):
        pass

    def _on_added(self, obj):
        pass

    def _meta_base_manager__insert(self, objects, *_, **__):
        pass

    def _base_manager__insert(self, objects, *_, **__):
        pass

    def _do_update(self, *args, **_):
        pass

    def delete(self, *_args, **_kwargs):
        pass
