import json
import sys
from .Loader import Loader
from ..EnvModifier import EnvModifier

class UnexpecteJsonContentError(Exception):
    """Unexpected json content error."""

class JsonLoader(Loader):
    """
    Json launcher loader.
    """

    def loadFromJson(self, jsonContents):
        """
        Load a launcher information from json.

        Expected format:
        {
          "launcherType": "bin",
          "config": {
            "executable": "/usr/bin/foo"
          },
          "env": {
            "prepend": {
              "PYTHONPATH": [
                "..."
              ]
            },
            "append": {
              "SOMETHINGELSE": [
                "..."
              ]
            },
            "override": {
              "TEST": "...",
              "FOO": [
                "..."
              ]
            },
            "unset": [
              "..."
            ]
          },
          "addons": {
            "name": {
              "env": {
                "prepend": {
                  "PYTHONPATH": [
                    "..."
                  ]
                }
              }
            }
          }
        }
        """
        contents = json.loads(jsonContents)

        # root checking
        if not isinstance(contents, dict):
            raise UnexpecteJsonContentError('Expecting object as root!')

        # launcher type
        if 'launcherType' not in contents:
            raise UnexpecteJsonContentError('Expecting luncher type!')

        self.setLauncherType(contents['launcherType'])

        self.__parseConfigContents(contents)
        self.__parseEnvContents(contents)
        self.__parseAddonContents(contents)

    def loadFromJsonFile(self, jsonFilePath):
        """
        Load the launcher information from a json file.

        {@link loadFromJson}
        """
        with open(jsonFilePath, 'r') as f:
            contents = f.read()
            try:
                self.loadFromJson(contents)
            except Exception as e:
                sys.stderr.write('Error on loading launcher file: {}\n'.format(jsonFilePath))
                raise e

    def __parseConfigContents(self, contents):
        """
        Parse the config from the contents.
        """
        if 'config' not in contents:
            return

        if not isinstance(contents['config'], dict):
            raise UnexpecteJsonContentError(
                'Expecting an object for the config!'
            )

        for configName, configValue in contents['config'].items():
            self.setLauncherConfig(configName, configValue)

    def __parseEnvContents(self, contents):
        """
        Parse the env from the contents.
        """
        if 'env' not in contents:
            return

        env = contents['env']
        envModifier = self.softwareEnvModifier()
        self.__parseEnv(env, envModifier)

    def __parseAddonContents(self, contents):
        """
        Parse the addon from the contents.
        """
        if 'addons' not in contents:
            return

        if not isinstance(contents['addons'], dict):
            raise UnexpecteJsonContentError(
                'Expecting an object for the addons!'
            )

        for addonName in contents['addons'].keys():
            if not isinstance(contents['addons'][addonName], dict):
                raise UnexpecteJsonContentError(
                    'Expecting an object for the addon!'
                )

            if 'env' in contents['addons'][addonName]:
                addonEnv = contents['addons'][addonName]['env']
                addonEnvModifier = EnvModifier()
                self.__parseEnv(addonEnv, addonEnvModifier)
                self.setAddonEnvModifier(addonName, addonEnvModifier)

    def __parseEnv(self, data, envModifier):
        """
        Parse an environment data to EnvModifier.
        """
        if not isinstance(data, dict):
            raise UnexpecteJsonContentError(
                'Expecting an object for the env!'
            )

        self.__parsePrepend(data, envModifier)
        self.__parseAppend(data, envModifier)
        self.__parseOverride(data, envModifier)
        self.__parseUnset(data, envModifier)

    def __parsePrepend(self, data, envModifier):
        """
        Parse the prepend data to the endModifier.

        @private
        """
        if 'prepend' not in data:
            return

        if not isinstance(data, dict):
            raise UnexpecteJsonContentError(
                'Expecting an object to describe the prepend vars!'
            )
        for varName, varValue in data['prepend'].items():
            envModifier.addPrependVar(varName, varValue)

    def __parseAppend(self, data, envModifier):
        """
        Parse the append data to the endModifier.

        @private
        """
        if 'append' not in data:
            return

        if not isinstance(data['append'], dict):
            raise UnexpecteJsonContentError(
                'Expecting an object to describe the append vars!'
            )
        for varName, varValue in data['append'].items():
            envModifier.addAppendVar(varName, varValue)

    def __parseOverride(self, data, envModifier):
        """
        Parse the override data to the endModifier.

        @private
        """
        if 'override' not in data:
            return

        if not isinstance(data['override'], dict):
            raise UnexpecteJsonContentError(
                'Expecting an object to describe the override vars!'
            )
        for varName, varValue in data['override'].items():
            envModifier.setOverrideVar(varName, varValue)

    def __parseUnset(self, data, envModifier):
        """
        Parse the unset data to the endModifier.

        @private
        """
        if 'unset' not in data:
            return

        if not isinstance(data['unset'], list):
            raise UnexpecteJsonContentError(
                'Expecting an array to describe the unset vars!'
            )
        for varName in data['unset']:
            envModifier.addUnsetVar(varName)
