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
"""Wrapped dulwich functions for processing git repo configs

"""
from os import makedirs
from os.path import (
    join as join_path,
    exists
)
from yaml import (
    safe_dump,
    YAMLError
)
# from dulwich.porcelain import (
#    clone,
#    checkout_branch,
#    pull,
#    branch_list
# )
from vtds_base import (
    read_config,
    ContextualError
)


class GitConfig:
    """Configuration from a git repo

    """
    def __init__(self, url, version, build_dir):
        """Constructor...

        """
        self.url = url
        self.version = version
        self.git_dir = join_path(build_dir, 'core', 'git')
        self.repo_dir = None
        try:
            makedirs(self.git_dir)
        except OSError as err:
            raise ContextualError(
                "cannot create directory for git configs '%s' - %s" % (
                    self.git_dir, str(err)
                )
            ) from err

    def retrieve(self, config_path):
        """Retrieve the repo at the specified URL if necessary and
        return the configuration in the file at the relative path in
        the repo specified by 'config_path'.

        """
        repo_map = {}
        repo_map_file = join_path(self.git_dir, '.repo_map.yaml')
        if exists(repo_map_file):
            # Not really a config file, but it doesn't know that. It
            # is a YAML file, so I can read it.
            repo_map = read_config(repo_map_file)
        repo_name = repo_map.get(self.url, None)
        if repo_name is None:
            repo_name = self.clone()
            repo_map[self.url] = repo_name
            try:
                with open(repo_map_file, 'w', encoding='UTF-8'):
                    safe_dump(repo_map, repo_map_file)
            except (OSError, YAMLError) as err:
                raise ContextualError(
                    "failed to re-write cached GIT repo map file '%s' - %s" % (
                        repo_map_file, str(err)
                    )
                ) from err
        self.checkout()
        file_path = join_path(self.repo_dir, config_path)
        return read_config(file_path)

    def clone(self):
        """Clone the repo that this object refers to.

        """
        repo_name = self.url.split('/')[-1]
        self.repo_dir = join_path(self.git_dir, repo_name)
        print("cloning '%s' into '%s'" % (self.url, repo_name))
        return repo_name

    def checkout(self):
        """Check out a specific version of the config repo and make
        sure it is up to date with the remote repo.

        """
        print(
            "checking out '%s' in '%s' (remote is '%s'" % (
                self.version, self.repo_dir, self.url
            )
        )
