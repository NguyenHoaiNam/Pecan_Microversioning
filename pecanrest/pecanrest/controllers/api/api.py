import pecan
from pecan import rest

class ApiController(rest.RestController):
    @pecan.expose()
    def _route(self, args):
	return super(ApiController, self)._route(args)
