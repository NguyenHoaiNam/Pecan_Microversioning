import six
import exc
import pecanrest.controllers.api.version as version

import operator

from pecan import rest
from pecan import request
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


VER_METHOD_ATTR = 'versioned_methods'

class ControllerMetaclass(type):
    """
    - This class automates the task of assenbling a dict that maps
    action keys to method names
    """

    def __new__(cls, name, bases, cls_dict):
        """ Adds version fuction dict to the class"""

        versioned_methods = None

        for base in bases:
            if base.__name__ == "Controller":

                # NOTE(cyeoh): This resets the VER_METHOD_ATTR attribute
                # between API controller class creations. This allows us
                # to use a class decorator on the API methods that doesn't
                # require naming explicitly what method is being versioned as
                # it can be implicit based on the method decorated. It is a bit
                # ugly
                if VER_METHOD_ATTR in base.__dict__:
                    versioned_methods = getattr(base, VER_METHOD_ATTR)

                    # Removes versioned methods so that next metaclass creation will have
                    # a clean start.
                    delattr(base, VER_METHOD_ATTR)
        if versioned_methods:
            cls_dict[VER_METHOD_ATTR] = versioned_methods

        return super(ControllerMetaclass, cls).__new__(cls, name, bases,
                                                       cls_dict)

class VersionedMethod(object):

    def __init__(self, name, start_version, end_version, func):
        """Versioning information for a single method

        @name: Name of the method
        @start_version: Minimum acceptable version
        @end_version: Maximum acceptable_version
        @func: Method to call

        Minimum and maximums are inclusive
        """
        self.name = name
        self.start_version = start_version
        self.end_version = end_version
        self.func = func

    def __str__(self):
        return ("Version Method %s: min: %s, max: %s"
                % (self.name, self.start_version, self.end_version))

@six.add_metaclass(ControllerMetaclass)
class Controller(rest.RestController):

    version = None

    def __getattribute__(self, key):

        def version_select():
            """Select the correct methods bases on the version

            :return: The correct versioned method
            """

            from pecan import request
            version = request.version

            func_list = self.versioned_methods[key]
            if version:
                for func in func_list:
                    if version.matches(func.start_version, func.end_version):
                        return func.func

            raise exc.HTTPNotAcceptable(_(
                 "Version %(ver)s was requested but the requested API %(api)s "
                 "is not supported for this version.") % {'ver': version,
                                                          'api': key})

        try:
            version_meth_dict = object.__getattribute__(self,VER_METHOD_ATTR)

        except AttributeError:
            # No versioning on this class
            return object.__getattribute__(self, key)

        if version_meth_dict and key in version_meth_dict:
            return version_select().__get__(self, self.__class__)

        return object.__getattribute__(self, key)


    @classmethod
    def api_version(cls, min_ver, max_ver=None):

        def decorator(f):
            obj_min_ver = version.Version('', '', '', min_ver)
            if max_ver:
                obj_max_ver = version.Version('', '', '', max_ver)
            else:
                obj_max_ver = version.Version('', '', '',
                                               version.CURRENT_MAX_VER)

            # Get the name of versioned method
            func_name = f.__name__

            # Create a new versioned method
            new_func = VersionedMethod(func_name, obj_min_ver, obj_max_ver, f)

            func_dict = getattr(cls, VER_METHOD_ATTR, {})

            if not func_dict:
                setattr(cls, VER_METHOD_ATTR, func_dict)

            func_list = func_dict.get(func_name, [])
            if not func_list:
                func_dict[func_name] = func_list
            func_list.append(new_func)

            is_intersect = Controller.check_for_versions_intersection(func_list)
            if is_intersect:
                # raise exception.ApiVersionsIntersect(
                #     name=new_func.name,
                #     min_ver=new_func.start_version,
                #     max_ver=new_func.end_version
                # )
                raise ValueError("Wrong value")

                # Ensure the list is sorted by minimum version (reversed)
                # so later when we work through the list in order we find
                # the method which has the latest version which supports
                # the version requested.

            func_list.sort(key=lambda f: f.start_version, reverse=True)

            return f

        return decorator

    @staticmethod
    def check_for_versions_intersection(func_list):
        """Determines whether function list intersections
        General algorithm:
        https://en.wikipedia.org/wiki/Intersection_algorithm
        :param func_list: list of VersionedMethod objects
        :return: boolean
        """

        pairs = []
        counter = 0

        for f in func_list:
            pairs.append((f.start_version, 1))
            pairs.append((f.end_version, -1))

        pairs.sort(key=operator.itemgetter(1), reverse=True)
        pairs.sort(key=operator.itemgetter(0))

        for p in pairs:
            counter += p[1]

            if counter > 1:
                return True







