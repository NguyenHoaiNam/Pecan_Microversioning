import pecanrest.controllers.api.controller as controller
import pecanrest.controllers.api.version as version
import pecan
from pecan import rest, response

from pecan import request

MIN_VER_STR = '%s %s' % (version.Version.service_string, version.BASE_VER)

MAX_VER_STR = '%s %s' % (version.Version.service_string, version.CURRENT_MAX_VER)

class RoutedController(controller.Controller):

    @controller.Controller.api_version('1.1', '1.10')
    @pecan.expose("json")
    def post(self, **kwds):
	response.status = 201
        result = {"vietstack":"It is the version from 1.1 to 1.10"}
	return result

    @controller.Controller.api_version('1.11')
    @pecan.expose("json")
    def post(self, **kwds):
	response.status = 201
        result = { "vietstack":"It is the version 1.11"}
	return result
    @pecan.expose("json")
    def get(self):
        response.status = 201
        result = { "vietstack":"It is the GET method"}
        return result

    @pecan.expose("json")
    def _route(self, args):
        ver = version.Version(pecan.request.headers, MIN_VER_STR, MAX_VER_STR)

        # settign the basic version header

        pecan.response.headers[version.Version.min_string] = MIN_VER_STR
        pecan.response.headers[version.Version.max_string] = MAX_VER_STR

        pecan.request.version = ver

        return super(RoutedController, self)._route(args)
