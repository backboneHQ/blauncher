import bver
from ..EnvModifier import EnvModifier
from ..Launcher import Launcher

# compatibility with python 2/3
try:
    basestring
except NameError:
    basestring = str

class MissingLauncherTypeError(Exception):
    """Missing launcher type error."""

class Loader(object):
    """
    Abstract launcher loader.
    """

    def __init__(self, software):
        """
        Create a parser.
        """
        self.__launcherType = None
        self.__launcherConfig = {}
        self.__softwareEnvModifier = EnvModifier()
        self.__addonsEnvModifier = {}
        self.__setSoftware(software)

    def software(self):
        """
        Return the software associated with the loader.
        """
        return self.__software

    def setLauncherType(self, registeredType):
        """
        Set the type of launcher (used to factory the launcher).
        """
        assert isinstance(registeredType, basestring), \
            "Invalid type!"

        self.__launcherType = registeredType

    def setLauncherConfig(self, name, value):
        """
        Set a configuration for the launcher.
        """
        self.__launcherConfig[name] = value

    def setAddonEnvModifier(self, addonName, envModifier):
        """
        Set an env modifier for the input addon name.

        This environment gets combined with the final environment when
        addon is enabled.
        """
        assert isinstance(envModifier, EnvModifier), \
            "Invalid EnvModifier Type!"

        self.__addonsEnvModifier[addonName] = envModifier

    def softwareEnvModifier(self):
        """
        Set an env modifier for the software.
        """
        return self.__softwareEnvModifier

    def launcher(self, env=None):
        """
        Return a launcher instance.
        """
        if not self.__launcherType:
            raise MissingLauncherTypeError(
                'Could not parse launcher, missing launcher type!'
            )

        finalEnv = dict(env) if env is not None else {}
        finalEnvModifier = EnvModifier(finalEnv)

        # software env
        finalEnvModifier.addFromEnvModifier(self.softwareEnvModifier())

        # addon env
        for addonName in self.software().addonNames():

            # checking if addon is enabled
            addon = self.software().addon(addonName)
            enabled = 'enabled' in addon.optionNames() and addon.option('enabled')

            # including addon env to the final env
            if enabled and addonName in self.__addonsEnvModifier:
                finalEnvModifier.addFromEnvModifier(self.__addonsEnvModifier[addonName])

        return Launcher.create(
            self.__launcherType,
            self.software(),
            finalEnvModifier.generate(),
            self.__launcherConfig
        )

    def __setSoftware(self, software):
        """
        Set the software that should be associated with the loader.
        """
        assert isinstance(software, bver.Versioned.Software), \
            "Invalid software type!"

        self.__software = software
