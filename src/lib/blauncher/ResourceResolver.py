import sys
import subprocess

class ResolveError(Exception):
    """Resolve error."""

class ResourceResolver(object):
    """
    Resolves a value containing bash functions and environment variables.
    """

    def __init__(self, env=None):
        """
        Create a value resolver object.
        """
        self.__setEnv(env or {})

    def env(self):
        """
        Return the environment being used by the resolver.
        """
        return self.__env

    def resolve(self, value):
        """
        Return a processed value.

        By resolving value of environments "$VAR" and commands "$(command)".
        """
        # in case there is nothing to be resolved
        if '$' not in value:
            return value

        # otherwise process the value. Using shell to be able to process
        # any commands $(command) that can be part of the unresolved value
        process = subprocess.Popen(
            'echo {0}'.format(value),
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            env=self.env(),
            shell=True
        )

        output, error = process.communicate()
        output = output.decode('ascii')

        # in case of any errors
        if error:
            raise ResolveError(error)

        # cleaning result, removing "\n" from the end of the result
        if output.endswith("\n"):
            output = output[:-1]

        return output

    def __setEnv(self, env):
        """
        Set the environment that should be used by the resolver.
        """
        self.__env = env
