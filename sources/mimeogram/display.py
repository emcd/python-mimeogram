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


''' System pager interaction. '''


from __future__ import annotations

from . import __


_scribe = __.produce_scribe( __name__ )


def discover_pager( ) -> str:
    ''' Discovers pager from environment and other places. '''
    from shutil import which
    # TODO: Better default for Windows.
    pager = __.os.environ.get( 'PAGER', 'less' )
    # TODO: Platform-specific list.
    for pager_ in ( pager, 'less', 'more' ):
        if which( pager_ ): return pager_
    from .exceptions import ProgramAbsenceError
    raise ProgramAbsenceError( 'pager' )


def display_content( content: str, *, suffix: str = '.txt' ) -> None:
    ''' Displays content via system pager. '''
    from .exceptions import PagerFailure, ProgramAbsenceError
    try: pager = discover_pager( )
    except ProgramAbsenceError:
        _scribe.warning( "Could not find pager program for display." )
        print( f"\n\n{content}\n\n" )
        input( "Press Enter to continue..." )
        return
    import subprocess # nosec B404
    import tempfile
    with tempfile.NamedTemporaryFile( mode = 'w', suffix = suffix ) as tmp:
        tmp.write( content )
        tmp.flush( )
        try: __.subprocess_execute( pager, tmp.name )
        except subprocess.SubprocessError as exc:
            raise PagerFailure( cause = exc ) from exc
