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
from shutil import rmtree
from dulwich.porcelain import (
    clone,
    checkout_branch
)
from dulwich.repo import Repo
from dulwich.objects import (
    Tag,
    Commit
)
from vtds_base import (
    read_config,
    ContextualError
)


class GitConfigs:
    """Container for the list and state of git configuration repos.

    """
    def __init__(self, build_dir):
        """Constructor: prepare a place for repos to live and
        initialize the list and state of the repos.

        """
        self.repos = {}
        self.repos_dir = join_path(build_dir, "core", "configs", "git")
        if exists(self.repos_dir):
            try:
                rmtree(self.repos_dir)
            except OSError as err:
                raise ContextualError(
                    "cannot remove git configs tree '%s' - %s" % (
                        self.repos_dir, str(err)
                    )
                ) from err
        try:
            makedirs(self.repos_dir)
        except OSError as err:
            raise ContextualError(
                "cannot create git configs tree '%s' - %s" % (
                    self.repos_dir, str(err)
                )
            ) from err

    def add_config(self, url):
        """Create or learn a directory to contain the repo found at
        the specified URL under the specified build directory tree.

        """
        # If we already know the repo, return the path to it
        if url in self.repos:
            return self.repos[url]
        # Don't know it, need to make the dir for it.
        repo_name = url.split('/')[-1].removesuffix('.git')
        repo_path = join_path(
            self.repos_dir, repo_name
        )
        self.repos[url] = (repo_name, repo_path)
        try:
            makedirs(repo_path)
        except OSError as err:
            raise ContextualError(
                "cannot create git config repo directory '%s' - %s" % (
                    repo_path, str(err)
                )
            ) from err
        return (repo_name, repo_path)


class GitConfig:
    """Configuration from a git repo

    """
    # Class variable to keep track of the container we are putting all
    # GitConfig instances into.
    configs = None

    def __init__(self, url, version, build_dir):
        """Constructor...

        """
        GitConfig.configs = (
            GitConfigs(build_dir) if GitConfig.configs is None else
            GitConfig.configs
        )
        self.url = url
        self.version = bytes(version, 'UTF-8') if version is not None else None
        self.default_version = version is None
        self.repo_name, self.git_dir = GitConfig.configs.add_config(self, url)
        self.repo = None

    def _clone(self):
        """Clone the repo that this object refers to.

        """
        if self.repo is not None:
            # Already cloned, don't try to do it again
            return
        try:
            clone(self.url, target=self.git_dir)
        except Exception as err:
            raise ContextualError(
                "error cloning GIT configuration repo '%s "
                "into directory '%s' = %s" % (
                    self.url, self.git_dir, str(err)
                )
            ) from err
        self.repo = Repo(self.git_dir)

    def _get_object(self, sha):
        """Given a SHA1 return the object from the repo corresponding
        to that SHA1.

        """
        try:
            return self.repo.get_object(sha)
        except Exception as err:
            raise ContextualError(
                "cannot find the object for SHA1 '%s' in '%s' at '%s'" % (
                    sha, self.url, self.git_dir
                )
            ) from err

    def _commit_from_sha(self, sha):
        """Deconstruct a tag SHA1 (which could be a Commit or a Tag)
        and get the commit from it.

        """
        obj = self._get_object(sha)
        if not isinstance(obj, (Tag, Commit)):
            raise ContextualError(
                "SHA1 '%s' derived from requested version '%s' in '%s' "
                "at '%s' is neither a Commit nor a Tag" % (
                    sha, self.version, self.url, self.git_dir
                )
            )
        return sha if not isinstance(obj, Tag) else obj.object[1]

    @staticmethod
    def _remote_branch(ref):
        """Based on the name of a ref, determine if it is a remote
        branch and return True if it is, False if it is not.

        """
        return ref.startswith(b'refs/remote')

    @staticmethod
    def _local_branch(ref):
        """Based on the name of a ref, determine if it is a local
        branch and return True if it is, False if it is not.

        """
        return ref.startswith(b'refs/heads')

    @staticmethod
    def _local_head(ref):
        """Based on the name of a ref, determine if it is a local
        branch and return True if it is, False if it is not.

        """
        return ref == b'HEAD'

    @staticmethod
    def _tag(ref):
        """Based on the name of a ref, determine if it is a tag and
        return True if it is and False if it is not.

        """
        return ref.startswith(b'refs/tags')

    def _get_version(self):
        """Check out the branch or tag that the version refers to. If
        no version, we take the default (do nothing here).

        """
        if self.default_version or self.version == b"HEAD":
            # Either no version is known yet for this repo, or the
            # user requested HEAD (which we interpret at the remote
            # HEAD since the local HEAD floats). Set the version to
            # the remote HEAD symref branch.
            symrefs = self.repo.refs.get_symrefs()
            self.version = (
                symrefs[b'refs/remotes/origin/HEAD'].split(b'/')[-1]
            )
        true_version = self.version
        for ref, sha in self.repo.get_refs().items():
            if self._local_head(ref):
                # Skip the local HEAD, since that will point to the
                # most recently selected branch which is useless to
                # us...
                continue
            if ref.split(b'/')[-1] != self.version:
                # This ref is not our version...
                continue
            if self._local_branch(ref):
                # Already have the local branch
                break
            if self._remote_branch(ref):
                # It's a remote branch, so make a local branch from it
                ref = (self.version, sha)
                self.repo.refs.add_if_new(*ref)
                break
            # We know we matched something, must be a tag: get the
            # real commit from the tag
            true_version = self._commit_from_sha(sha)
            break
        # Okay, either we matched something above and set things up
        # the way we want, or the version selected is either a SHA1 or
        # not a real branch or tag. At this point, it doesn't really
        # matter. Try to check it out, and if it fails report a
        # problem.
        try:
            checkout_branch(self.repo, true_version)
        except Exception as err:
            raise ContextualError(
                "unable to check-out version '%s' of '%s' in '%s' - %s" % (
                    self.version, self.url, self.git_dir, str(err)
                )
            ) from err

    def retrieve(self, config_path):
        """Retrieve the repo at the specified URL if necessary and
        return the configuration in the file at the relative path in
        the repo specified by 'config_path'. The value of 'config_path'
        is a relative pathname separated by forward slashes ('/').

        """
        self._clone()
        self._get_version()
        file_path = join_path(self.git_dir, config_path)
        return read_config(file_path)
