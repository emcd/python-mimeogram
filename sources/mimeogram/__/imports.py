# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Common imports and type aliases used throughout the package. '''

# pylint: disable=unused-import
# ruff: noqa: F401


from __future__ import annotations

import abc
import asyncio
import collections.abc as cabc
import enum
import os
import re
import sys
import types

from dataclasses import dataclass
from logging import getLogger as produce_scribe
from pathlib import Path

import aiofiles
import httpx
import magic
import typing_extensions as typx


ComparisonResult: typx.TypeAlias = bool | types.NotImplementedType
