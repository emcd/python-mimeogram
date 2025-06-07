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


''' Common imports used throughout the package. '''

# ruff: noqa: F401


import abc
import asyncio
import collections.abc as cabc
import enum
import os
import re
import sys
import types

from contextlib import AsyncExitStack as ExitsAsync
from dataclasses import (
    dataclass,
    field as dataclass_declare,
)
from logging import getLogger as produce_scribe
from pathlib import Path
from uuid import uuid4

import typing_extensions as typx
# --- BEGIN: Injected by Copier ---
import tyro
# --- END: Injected by Copier ---

from absence import Absential, absent, is_absent
from accretive.qaliases import AccretiveDictionary
from frigid.qaliases import (
    ImmutableClass,
    ImmutableDictionary,
    ImmutableObject,
    ImmutableProtocolClass,
    reclassify_modules_as_immutable,
)
from platformdirs import PlatformDirs


@typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ImmutableStandardDataclass( ImmutableClass ):
    ''' Metaclass for immutable standard dataclasses. (Typechecker hack.) '''


@typx.dataclass_transform( frozen_default = True, kw_only_default = True )
class ImmutableStandardProtocolDataclass( ImmutableProtocolClass ):
    ''' Metaclass for immutable standard dataclasses. (Typechecker hack.) '''


simple_tyro_class = tyro.conf.configure( )
standard_dataclass = dataclass( frozen = True, kw_only = True, slots = True )
standard_tyro_class = tyro.conf.configure( tyro.conf.OmitArgPrefixes )
