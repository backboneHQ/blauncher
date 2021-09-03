from ..ProcessExecution import ProcessExecution
from bver.Versioned import Software

class MissingRequiredConfigError(Exception):
    """Undefined required config error."""

class InvalidConfigError(Exception):
    """Invalid config error."""

class LauncherNotRegisteredError(Exception):
    """Launcher not registered error."""

class Launcher(object):
    """
    Abstract launcher.
    """

    __registered = {}

    def __init__(self, software, env=None, config=None):
        """
        Create a launcher.
        """
        self.__setSoftware(software)
        self.__setEnv(env or {})

        # setting launcher config
        self.__config = {}
        for name, value in (config or {}).items():
            self.__setConfig(name, value)

        # checking required config
        for requiredName in self.requiredConfigNames():
            if requiredName not in self.configNames():
                raise MissingRequiredConfigError(
                    'Required config "{0}" has not been defined!'.format(
                        requiredName
                    )
                )

    def software(self):
        """
        Return the software instance that should be used by the launcher.
        """
        self.__software

    def config(self, name):
        """
        Return the value for a config.
        """
        if name not in self.__config:
            raise InvalidConfigError(
                'Invalid config "{0}"'.format(name)
            )

        return self.__config[name]

    def configNames(self):
        """
        Return a list of config names.
        """
        return self.__config.keys()

    def env(self):
        """
        Return the environment for the launcher.
        """
        return self.__env

    def run(self, executableType="default", **kwargs):
        """
        Perform launcher.

        TODO: The idea is to collect as much information as possible about the
        execution, such as stdout, stderr, session time, processing peak, memory
        peak (etc) and store them in the database.
        """
        processExecution = self._perform(executableType, **kwargs)

        assert isinstance(processExecution, ProcessExecution), \
            'Invalid ProcessExecution Type!'

        # \todo: notify blauncher daemon about:
        # processExecution.pid()

        processExecution.execute()

        # \todo: store in database:
        # processExecution.exitStatus()
        # processExecution.stdout()
        # processExecution.stderr()

        return processExecution

    def _perform(self, executableType, **kwargs):
        """
        Run the launcher.

        Should be re-implemented by derived classes to perform the execution
        of the launcher and return ProcessExecution object.
        """
        raise NotImplemented

    @staticmethod
    def create(name, *args, **kwargs):
        """
        Launcher factory.
        """
        if name not in Launcher.__registered:
            raise LauncherNotRegisteredError(
                'Invalid launcher type "{0}"'.format(name)
            )

        launcherInstance = Launcher.__registered[name](*args, **kwargs)
        return launcherInstance

    @staticmethod
    def register(launcherClass, name):
        """
        Register a launcher type.

        It can be factored later via {@link create}
        """
        assert issubclass(launcherClass, Launcher), "Invalid Launcher class!"

        Launcher.__registered[name] = launcherClass

    @staticmethod
    def registeredNames():
        """
        Return a list of registered launcher types.
        """
        return Launcher.__registered.keys()

    @classmethod
    def requiredConfigNames(cls):
        """
        Return a list of required config for the launcher implementation.
        """
        return []

    def __setSoftware(self, software):
        """
        Set the software that should be launched.
        """
        assert isinstance(software, Software), \
            "Invalid software type"

        self.__software = software

    def __setEnv(self, env):
        """
        Set the environment for the launcher.
        """
        self.__env = env

    def __setConfig(self, name, value):
        """
        Set a value under the config.
        """
        self.__config[name] = value
