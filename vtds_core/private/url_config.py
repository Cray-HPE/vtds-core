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
"""Wrapped functions for retrieving and decoding configs from URLs.

"""
from yaml import (
    safe_load,
    YAMLError
)
from requests import get as url_get
from vtds_base import ContextualError

HEADERS = {
    'Content-Type': 'text/plain',
    'Accept': 'text/plain'
}


def read_url_config(url):
    """Read in a configuration file from a URL and return the
       parsed collection from that file.

    """
    response = url_get(url, headers=HEADERS, verify=True, timeout=600)
    if not response.ok:
        raise ContextualError(
            "failed to retrieve '%s' "
            "(status_code=%d, text='%s', reason='%s')" % (
                url, response.status_code, response.text, response.reason
            )
        )
    try:
        return safe_load(response.text)
    except YAMLError as err:
        raise ContextualError(
            "failed to parse YAML file found at '%s' - %s" % (
                url, str(err)
            )
        ) from err
