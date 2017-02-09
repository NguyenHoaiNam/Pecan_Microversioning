#import exc

from webob import exc

CURRENT_MAX_VER = '1.11'
BASE_VER = '1.1'


class Version(object):
    string = 'X-Vietstack-Api-Version'

    min_string = 'Vietstack-Api-Min-Version'

    max_string = 'Vietstack-Api-Max-Version'

    service_string = 'Microversion'

    def __init__(self, headers, default_version, latest_version, from_string=None):
        """Create an API Version object from the supplied headers.

        :param headers: webob headers
        :param default_version: version to use if not specified in headers
        :param latest_version: version to use if latest is requested
        :param from_string: create the version from string not headers
        :raises: webob.HTTPNotAcceptable
        """

        if from_string:
            (self.major, self.minor) = tuple(int(i)
                                             for i in from_string.split('.'))

        else:
            (self.major, self.minor) = self.parse_headers(headers,
                                                          default_version,
                                                          latest_version)

    @staticmethod
    def parse_headers(headers, default_version, latest_version):
        """Determine the API version requested based on the headers supplied.
        :param headers: webob headers
        :param default_version: version to use if not specified in headers
        :param latest_version: version to use if latest is requested
        :returns: a tuple of (major, minor) version numbers
        :raises: webob.HTTPNotAcceptable
        """

	if Version.string not in headers.keys():
	    raise exc.HTTPNotAcceptable("Invalid header type for %s header" % Version.string) 
        
	version_header = headers.get(Version.string, default_version)

        try:
            version_service, version_str = version_header.split()
        except ValueError:
            raise exc.HTTPNotAcceptable(_(
                "Invalid service type for %s header") % Version.string)

        if version_str.lower() == "latest":
            version_service, version_str = latest_version.split()

        try:
            version = tuple(int(i) for i in version_str.split('.'))
        except ValueError:
            version = ()

        if len(version) != 2:
            # raise exc.HTTPNotAcceptable(_(
            #     "Invalid value for %s header") % Version.string)
            raise ValueError
        return version


    def is_null(self):
        return self.major == 0 and self.minor == 0

    def matches(self, start_version, end_version):
        if self.is_null():
            raise ValueError

        return start_version <= self <= end_version

    def __lt__(self, other):
        if self.major < other.major:
            return True
        if self.major == other.major and self.minor < other.minor:
            return True
        return False

    def __gt__(self, other):
        if self.major > other.major:
            return True
        if self.major == other.major and self.minor > other.minor:
            return True
        return False

    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ge__(self, other):
        return self > other or self == other
