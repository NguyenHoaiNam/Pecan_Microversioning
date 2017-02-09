from pecanrest.controllers.api import api
from pecanrest.controllers.api import routed_controller
import pecanrest.controllers.api.version as version

MIN_VER_STR = '%s %s' % (version.Version.service_string, version.BASE_VER)

MAX_VER_STR = '%s %s' % (version.Version.service_string, version.CURRENT_MAX_VER)

import pecan
from pecan import rest, response
from pecan import expose, abort

class RootController(rest.RestController):
    @pecan.expose()
    def _route(self, args):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the magnum API
        if the version number is not specified in the url.
        """

        return super(RootController, self)._route(args)
    	#pass
    #@pecan.expose("json")
    #def _route(self, args):
    #    ver = version.Version(pecan.request.headers, MIN_VER_STR, MAX_VER_STR)

    #    # settign the basic version header

    #    pecan.response.headers[version.Version.min_string] = MIN_VER_STR
    #    pecan.response.headers[version.Version.max_string] = MAX_VER_STR

    #    pecan.request.version = ver

    #    return super(RootController, self)._route(args)


pecan.route(RootController, 'api', api.ApiController())
pecan.route(api.ApiController, 'v1', routed_controller.RoutedController())
