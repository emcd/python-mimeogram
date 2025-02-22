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


''' Exchange of MIME bundles with LLMs. '''


from . import __
from . import acquirers
from . import apply
from . import cli
from . import create
from . import differences
from . import display
from . import edit
from . import exceptions
from . import formatters
from . import interactions
from . import parsers
from . import updaters

# TODO: Export various module contents.


__version__ = '1.0'


def main( ):
    ''' Entrypoint. '''
    cli.execute( )


__.reclassify_modules_as_immutable( __name__ )
