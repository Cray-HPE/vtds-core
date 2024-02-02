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
from vtds_base import (
    entrypoint
)

USAGE_MSG = """
Some Usage Message here...
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
    print("thank you for using the vtds command... [%s]" % str(argv))


def entry():
    """Entry point for the wrapper. This sets up command line
    arguments for the wrapper and takes care of handling the vTDS
    exception classes to report errors. Other exceptions are allowed
    to pass to the runtime for handling.

    """
    entrypoint(USAGE_MSG, main)
