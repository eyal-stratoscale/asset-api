CONFIG_VERSION = 1
config = None


class Config:
    def __init__(self, obj):
        if 'CONFIG_VERSION' not in obj:
            raise Exception("Configuration file must contain 'CONFIG_VERSION' field")
        if obj['CONFIG_VERSION'] != CONFIG_VERSION:
            raise Exception("Expected CONFIG_VERSION to be %s found %s" % (
                CONFIG_VERSION, obj['CONFIG_VERSION']))
        if 'DEFAULT_USER' not in obj:
            raise Exception("Configuration file must contain 'DEFAULT_USER' field")
        self._defaultUser = obj['DEFAULT_USER']
        if 'DEFAULT_PURPOSE' not in obj:
            raise Exception("Configuration file must contain 'DEFAULT_PURPOSE' field")
        self._defaultPurpose = obj['DEFAULT_PURPOSE']
        if 'PROVIDER' not in obj:
            raise Exception("Configuration file must contain 'PROVIDER' field")
        self._provider = obj['PROVIDER']
        if 'DEFAULT_CONTINENT' not in obj:
            raise Exception("Configuration file must contain 'DEFAULT_CONTINENT' field")
        self._defaultContinent = obj['DEFAULT_CONTINENT']
        global config
        config = self

    def defaultUser(self):
        return self._defaultUser

    def defaultContinent(self):
        return self._defaultContinent

    def defaultPurpose(self):
        return self._defaultPurpose

    def provider(self):
        return self._provider
