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
"""Wrapper implementation for the vTDS driver commands.

"""
from os import (
    makedirs
)
from os.path import (
    abspath,
    exists,
    join as path_join
)
from getopt import (
    getopt,
    GetoptError
)
from vtds_base import (
    UsageError,
    ContextualError,
    entrypoint,
    read_config,
    merge_configs
)
from .runner import RequestRunner
from .base_config import BaseConfig

USAGE_MSG = """
Usage: vtds [OPTIONS] REQUEST [args]
Where 'OPTIONS' can be:

    -b,--build-dir=<path>

     Specify the path to the vTDS build tree to be used in building or
     managing your vTDS system. By default this will be a directory called
     'vtds-build' in the current working directory where this command is
     run.

    -C,--core-config=<file>

     Specify a vTDS 'core' configuration containing the vTDS layers
     used to compose the vTDS and, optionally, the configuration
     sources used to build the vTDS. This configuration is overlaid
     onto the default vTDS 'core' configuration. The annotated default
     'core' configuration can be gotten by running

         vtds base-config

     and examining the 'core:' block of the output. If this option is
     not supplied, the 'vtds' command will look for a file named
     'config.yaml' in the current working directory. If that file is
     not found, the 'vtds' command will simply use the default core
     configuration.

    -e,--env=<path>

     Specify a path to the where the virtual environment that contains the
     vTDS layeers and their dependencies should be found or created when
     running REQUEST. By default, this is created and expected in a 'venv'
     directory below the core directory in the vTDS build tree (see
     --build-dir).

    -r,--refresh

     Install a fresh set of vTDS layers and their dependencies for
     running requests.

    -h,--help

     Display this messge.

and REQUEST can be any of:

    validate

      Run a validation pass through all of the vTDS layers to verify
      the rough suitability of the layer state for deployment. While
      deployments may fail after running 'validate', this identifies
      issues that can be found through static analysis.

    deploy

      Deploy the vTDS system described in the configuraiton supplied.

    remove

      Release all resources associated with the vTDS system described
      in the configuration supplied.

    base_config

      Place the combined annotated base configuration text of all
      layers selected in the core configuration on standard
      output. This is provided to assist in designing configuration
      overlays to create a specific vTDS system.

    show_config

      Place the complete final configuration composed using the vTDS
      configuration you have designed on standard output.

      NOTE: This output is not annotated and the order of the items in
            it is not the same as what is found in the text
            configuration files.

The arguments to each REQUEST can be obtained by running

    vtds REQUEST --help
"""


def main(argv):
    """The main wrapper command implementation to set up and execute
    the vTDS core driver commands. This parses the command line to
    obtain the necessary information to create a python virtual
    environment and determine the vTDS request specified by the
    user. It then installs the core driver and all of the layers
    specified in the vtds-core configuration in that virtual
    environment and executes the request using the virtual
    environment.

    """
    try:
        optlist, args = getopt(
            argv,
            "b:C:e:hr",
            ["build-dir=", "core-config=", "env=", "refresh", "help"]
        )
    except GetoptError as err:
        raise UsageError(str(err)) from err
    if not args:
        raise UsageError("no request provided")
    build_dir = abspath('vtds-build')
    core_config = abspath("config.yaml")
    conf_file = core_config if exists(core_config) else None
    venv_path = None
    new_env_option = False
    for opt, arg in optlist:
        if opt in ['-b', '--build-dir']:
            build_dir = arg
        elif opt in ['-C', '--core-config']:
            conf_file = abspath(arg)
        elif opt in ['-e', '--env']:
            venv_path = arg
        elif opt in ['-r', '--refresh']:
            new_env_option = True
        elif opt in ['-h', '--help']:
            raise UsageError(None)
        else:
            raise UsageError("unprocessed option for core setup - '%s'" % opt)
    # create the 'core' build directory
    try:
        makedirs(path_join(build_dir, 'core'), exist_ok=True)
    except OSError as err:
        raise ContextualError(
            "failed to create 'core' build directory '%s' - %s" % (
                build_dir, str(err)
            )
        ) from err

    # Read in the core configuration...
    config = read_config(conf_file) if conf_file else {}
    base_config = BaseConfig().get_base_config()
    config = merge_configs(base_config, config)

    # Run the request
    venv_path = path_join(
        build_dir, 'core', 'venv'
    ) if venv_path is None else venv_path
    request_runner = RequestRunner(venv_path, build_dir, config)
    request = [args[0]]
    request += ['--build-dir=%s' % build_dir]
    request += (
        ['--core-config=%s' % conf_file] if conf_file and exists(conf_file)
        else []
    )
    request += args[1:] if len(args) > 1 else []
    # pylint: disable=fixme
    # XXX - NEED MORE ROBUST CHECKS HERE, BUT THIS WILL DO FOR NOW
    if not exists(venv_path) or new_env_option:
        request_runner.create_venv()
    request_runner.run_request(request)


def entry():
    """Entrypoint...

    """
    entrypoint(USAGE_MSG, main)


if __name__ == "__main__":
    entry()
