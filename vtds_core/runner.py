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
"""Virtual environment python runner mechanisms

"""
import sys
from os import makedirs
from os.path import join as path_join
from venv import EnvBuilder
from subprocess import (
    run,
    SubprocessError
)
from vtds_base import (
    ContextualError,
    logfile
)
from .private.git_modules import GitModule


class RequestRunner:
    """A class that provides the functionality of setting up a
    viretual environments and running python modules from within that
    virtual environment.

    """
    def __init__(self, venv_path, build_dir, config):
        """An environment in which to run vTDS requests that creates a
        python virtual environmment populated with the python version
        and the vTDS layers (and supporting dependencies) derived from
        the core config provided in `config`.

        """
        self.build_dir = build_dir
        self.venv = venv_path
        core = config.get('core', None)
        if core is None:
            raise ContextualError(
                "configuration does not contain a 'core' configuration"
            )
        self.layers = core.get('layers', None)
        if self.layers is None:
            raise ContextualError(
                "core configuration does not contain layer specifications"
            )
        self.env_builder = EnvBuilder(
            system_site_packages=False,
            clear=True,
            symlinks=True,
            upgrade=False,
            with_pip=False,
            prompt=None,
        )
        self.log_dir = path_join(self.venv, "vtds", "logs")

    def run_module(self, cmd, isolated=False, stdout=None, stderr=None):
        """Run a python module in the virtual environment where 'cmd'
           is a list of arguments starting with the name of the
           module. For example:

           ["pip", "install", "pyyaml"]

           Would run the above command using the python context
           defined by the virtual environment.

        """
        python = [path_join(self.venv, "bin", "python3")]
        python += ["-I"] if isolated else []
        python += ["-m"]
        with logfile(stdout) as outfile, logfile(stderr) as errfile:
            try:
                run(python + cmd, check=True, stdout=outfile, stderr=errfile)
            except (SubprocessError, OSError) as err:
                raise ContextualError(
                    "execution in virtual environment failed - %s" % str(err),
                    output=stdout,
                    error=stderr
                ) from err

    def run_request(self, request):
        """Run a vTDS request in the virtual environment.

        """
        request[0] = "vtds_core.private.%s" % request[0]
        self.run_module(request, stdout=sys.stdout, stderr=sys.stderr)

    def ensurepip(self):
        """Install pip in the virtualenv capturing output in output
        and error logs for analysis.

        """
        # Make sure pip is there using 'ensurepip'
        cmd = ["ensurepip", "--upgrade", "--default-pip"]
        stdout = path_join(self.log_dir, "ensure-pip-output.log")
        stderr = path_join(self.log_dir, "ensure-pip-errors.log")
        self.run_module(cmd, isolated=True, stdout=stdout, stderr=stderr)
        # Now bring pip up to data using 'pip install --upgrade'
        cmd = ["pip", "install", "--upgrade", "pip"]
        stdout = path_join(self.log_dir, "upgrade-pip-output.log")
        stderr = path_join(self.log_dir, "upgrade-pip-errors.log")
        self.run_module(cmd, isolated=True, stdout=stdout, stderr=stderr)

    def pypi_install_pkg(self, pkg, version=None, index=None):
        """Install the specified version of the sepcified package from
           a PyPI index into the virtual environment.

        """
        pkg_string = "%s%s" % (pkg, version) if version is not None else pkg
        cmd = ["pip", "install", pkg_string]
        if index:
            cmd += ['--extra-index-url', index]
        stdout = path_join(self.log_dir, "install-%s-output.log" % pkg)
        stderr = path_join(self.log_dir, "install-%s-errors.log" % pkg)
        self.run_module(cmd, stdout=stdout, stderr=stderr)

    def git_install_pkg(self, pkg, repo_url, version=None):
        """Install the specified version of the sepcified package from
           a git source repo into the virtual environment.

        """
        module = GitModule(repo_url, version, self.build_dir)
        repo_path = module.retrieve()
        cmd = ["pip", "install", repo_path]
        stdout = path_join(self.log_dir, "install-%s-output.log" % pkg)
        stderr = path_join(self.log_dir, "install-%s-errors.log" % pkg)
        self.run_module(cmd, stdout=stdout, stderr=stderr)

    def install_pkg(self, name, layer):
        """Install a layer or package based on information in the
        config.

        """
        pkg = layer.get('package', None)
        if pkg is None:
            raise ContextualError(
                "no package name given for layer '%s' "
                "in core config" % (name)
            )
        source_type = layer.get('source_type', "pypi")
        metadata = layer.get('metadata', {})
        if source_type == "pypi":
            version = metadata.get('version', None)
            index = metadata.get('url', None)
            self.pypi_install_pkg(pkg, version, index)
        elif source_type == 'git':
            version = metadata.get('version', None)
            repo_url = metadata.get('url', None)
            if repo_url is None:
                raise ContextualError(
                    "no repo URL given for GIT layer '%s' "
                    "in core config" % name
                )
            self.git_install_pkg(pkg, repo_url, version)
        else:
            raise ContextualError(
                "unknown source type '%s' found for package '%s'" % (
                    source_type, pkg
                )
            )

    def create_venv(self):
        """Create a virtual environment at the specified path and
           install the layers and their dependencies in that virtual
           environment.

        """
        try:
            self.env_builder.create(self.venv)
        except OSError as err:
            raise ContextualError(
                "cannot create virtual environment '%s' - %s" % str(err)
            ) from err

        # Create a logging directory inside the venv to give us a
        # place to keep logs of activities involved in setting up the
        # venv.
        try:
            makedirs(self.log_dir)
        except OSError as err:
            raise ContextualError(
                "failed to create virtual envirnoment log directory '%s' "
                "- %s" % (self.log_dir, str(err))
            ) from err

        # Make sure pip is installed. Do this here instead of
        # automagically as part of venv creation because I want to
        # capture the output in logs instead of on the console.
        self.ensurepip()

        # Install the layers from the config. First get the base
        # library if there is one listed. The rest will have a
        # dependency on it that may break if we don't install it
        # first.
        if 'base' in self.layers:
            self.install_pkg('base', self.layers['base'])
        # Now get the rest.
        for name, layer in self.layers.items():
            if name == 'base':
                continue
            self.install_pkg(name, layer)
