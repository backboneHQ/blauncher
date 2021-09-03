import os
import blauncher
import bver

class InvalidConfigDirError(Exception):
    """Invalid config dir error."""

class LauncherRunner(object):
    """
    High level launcher runner.
    """

    def __init__(self, software, blauncherConfigDir):
        """
        Create a launcher runner.
        """
        self.__setSoftware(software)
        self.__setLauncherConfigDir(blauncherConfigDir)

    def software(self):
        """
        Return the software associated with the runner.
        """
        return self.__software

    def __setLauncherConfigDir(self, configDir):
        """
        Set a path about where the configuration for the launchers is localized.
        """
        if not (os.path.exists(configDir) and os.path.isdir(configDir)):
            raise InvalidConfigDirError(
                'Invalid config directory "{0}"'.format(configDir)
            )

        self.__launcherConfigDir = configDir

    def launcherConfigDir(self):
        """
        Return a path about where the configuration for the launchers is localized.
        """
        return self.__launcherConfigDir

    def run(self, executableType, args=[], env=None):
        """
        Launch an application.
        """
        assert isinstance(args, list), \
            "Invalid args type"

        env = env or {}
        assert isinstance(env, dict), \
            "Invalid dict type"

        # try to find the application name under the configuration
        applicationConfiguration = os.path.join(
            self.launcherConfigDir(),
            '{0}.json'.format(self.software().name())
        )

        loader = blauncher.Loader.JsonLoader(self.software())

        # passing additional args to the process
        loader.setLauncherConfig(
            'args',
            args
        )

        loader.loadFromJsonFile(applicationConfiguration)
        launcher = loader.launcher(env)

        # running launcher
        return launcher.run(executableType)

    def __setSoftware(self, software):
        """
        Set the software that launched by the runner.
        """
        assert isinstance(software, bver.Versioned.Software), \
            "Invalid Software Type!"

        self.__software = software
