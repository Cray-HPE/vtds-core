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
#
# The request implementations are very boilerplate but most easy
# commonality has been removed. Tell lint it is okay...
#
# pylint: disable=duplicate-code
"""Deploy a proposed vTDS configuration.

"""
from os.path import (
    exists,
    abspath
)
from getopt import (
    getopt,
    GetoptError
)
from vtds_base import (
    UsageError,
    ContextualError,
    entrypoint
)
from .common import CoreCommon

USAGE_MSG = """
Usage: vtds [CORE-OPTIONS] verify [OPTIONS]

Where:
    CORE_OPTIONS are the options to the vTDS core, not described here. To
    see those, use 'vtds --help'.

    OPTIONS are:

    -c,--config=<file>

    Specify the path to the configuration overlay file you want to
    use to deploy your vTDS.

    This option can be used more than once, and each instance merges
    another configuration overlay onto the previously specified
    ones. The final merged product from all configuration files
    specified using this option becomes the 'command-line' type
    configuration in the configuration sources list from the 'core'
    configuration.

    By default, if no list of configuration sources is provided in the
    'vtds' command 'core' configuration, the files listed on the
    command line are applied in order followed by the 'core'
    configuration itself.

    -h,--help

    Dislpay this message
"""


def main(argv):
    """Deploy a vTDS configuration.

    """
    try:
        # The -b,--build-dir and -C,--core-config options are not part
        # of the public command line for this script. They should
        # always be passed in (if appropriate) by the wrapper (see
        # ../wrapper.py).
        optlist, _ = getopt(
            argv,
            "b:C:c:h",
            ["build-dir=", "core-config=", "config=", "help"]
        )
    except GetoptError as err:
        raise UsageError(str(err)) from err
    build_dir = None
    core_conf_file = None
    conf_files = []
    for opt, arg in optlist:
        if opt in ['-b', '--build-dir']:
            if build_dir is not None:
                raise UsageError(
                    "the -b,--build-dir option should only be supplied by the "
                    "'vtds' wrapper script, never on the command line"
                )
            build_dir = arg
            if not exists(build_dir):
                # Contextual because this option should only be specified
                # by the wrapper, and does not show up in the usage.
                raise ContextualError(
                    "requested build directory '%s' not found" % build_dir
                )
        elif opt in ['-C', '--core-config']:
            if core_conf_file is not None:
                raise UsageError(
                    "the -c,--core-config option should only be supplied "
                    "by the 'vtds' wrapper script, never on the command line"
                )
            core_conf_file = abspath(arg)
            if not exists(core_conf_file):
                # Contextual because this option should only be specified
                # by the wrapper, and does not show up in the usage.
                raise ContextualError(
                    "requested core configuration file '%s' "
                    "not found" % core_conf_file
                )
        elif opt in ['-c', '--config']:
            conf_files.append(abspath(arg))
            if not exists(conf_files[-1]):
                raise UsageError(
                    "requested configuration file '%s' "
                    "not found" % conf_files[-1]
                )
        elif opt in ['-h', '--help']:
            raise UsageError(None)
        else:
            raise UsageError("unprocessed option for core setup - '%s'" % opt)

    # Make sure we are (or appear to be) running under the wrapper...
    if build_dir is None or not exists(build_dir):
        raise ContextualError(
            "this request must be invoked through the 'vtds' wrapper"
        )

    # Get a vTDS stack to use
    stack = CoreCommon(build_dir).compose_stack(core_conf_file, conf_files)

    # Run the request...
    stack.consolidate()
    stack.prepare()
    stack.validate()
    stack.deploy()


def entry():
    """Entry point...

    """
    entrypoint(USAGE_MSG, main)


if __name__ == "__main__":
    entry()
