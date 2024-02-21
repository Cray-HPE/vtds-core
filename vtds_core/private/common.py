#
# MIT License
#
# (C) Copyright [2024] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Common support functions for vTDS requests.

"""
from os.path import (
    exists
)
from vtds_base import (
    read_config,
    merge_configs,
    VTDSStack,
    ContextualError
)
from .. import BaseConfig
from .git_config import GitConfig
from .url_config import read_url_config


class CoreCommon:
    """Common core setup for all vTDS requests.

    """
    def __init__(self, build_path):
        """ Constructor.

        """
        self.build_path = build_path

    def read_git_config(self, url, version, path):
        """Read in a 'git' style configuration file and return the
        parsed collection from that file.

        """
        repo = GitConfig(url, version, self.build_path)
        return repo.retrieve(path)

    def compose_full_config_overlay(self, core_config, cmd_config):
        """Using the core configuration provided and the fully resolved
        command line config overlay, compose the full vTDS configuration
        overlay to be applied on top of the base configuration once the
        stack has been created.

        """
        full_overlay = {}
        configs = core_config.get('core', {}).get('configurations', [])
        for config in configs:
            config_type = config.get('type', None)
            if config_type == 'core-config':
                full_overlay = merge_configs(full_overlay, core_config)
            elif config_type == 'command-line':
                full_overlay = merge_configs(full_overlay, cmd_config)
            elif config_type == 'git':
                metadata = config.get('metadata', {})
                url = metadata.get('repo', None)
                version = metadata.get('version', None)
                path = metadata.get('path', None)
                full_overlay = merge_configs(
                    full_overlay, self.read_git_config(url, version, path)
                )
            elif config_type == 'url':
                metadata = config.get('metadata', {})
                url = metadata.get('url', None)
                full_overlay = merge_configs(
                    full_overlay, read_url_config(url)
                )
            elif config_type == 'local-file':
                metadata = config.get('metadata', {})
                path = metadata.get('path', None)
                full_overlay = merge_configs(
                    full_overlay, read_config(path)
                )
            elif config_type is None:
                raise ContextualError(
                    "no 'type' specified for one of the configuration "
                    "sources in the core configuration"
                )
            else:
                raise ContextualError(
                    "unknown 'type' '%s' specified for one of the "
                    "configuration sources in the core "
                    "configuration" % config_type
                )
        return full_overlay

    def compose_stack(self, core_config_file, cmd_config_files):
        """Construct and initialize a vTDS stack based on the supplied
           core configuration file, if any, and the list of command
           line configuration files if any. Use the 'core'
           sub-directory within the build directory for staging
           configuration sources and any other core driver data.

        """
        # Read in the core configuration...
        core_config = read_config(
            core_config_file,
            "core configuration"
        ) if core_config_file and exists(core_config_file) else {}
        base_config = BaseConfig().get_base_config()
        core_config = merge_configs(base_config, core_config)

        # Compose the command line configuration overlay
        cmd_config = {}
        for config_file in cmd_config_files:
            config = read_config(config_file, "command line configuration")
            cmd_config = merge_configs(cmd_config, config)

        # Compose the final config overlay
        final_overlay = self.compose_full_config_overlay(
            core_config, cmd_config
        )

        # Set up the vtds stack
        layers = core_config.get('core', {}).get('layers', {})
        stack = VTDSStack(
            provider_name=layers.get('provider', {}).get('module', None),
            platform_name=layers.get('platform', {}).get('module', None),
            cluster_name=layers.get('cluster', {}).get('module', None),
            application_name=layers.get('application', {}).get('module', None)
        )
        base_config = stack.get_base_config()
        final_config = merge_configs(base_config, final_overlay)
        stack.initialize(final_config, self.build_path)
        return stack
