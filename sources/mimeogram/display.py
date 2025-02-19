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


def discover_pager( ) -> __.cabc.Callable[ [ str ], None ]:
    ''' Discovers pager and returns executor function. '''
    from shutil import which
    from subprocess import run # nosec B404
    pager = __.os.environ.get( 'PAGER', 'less' )
    for pager_ in ( pager, 'less', 'more' ):
        if ( pager := which( pager_ ) ):
            match __.sys.platform:
                case 'win32':
                    # Windows 'more.com' does not support UTF-8.
                    if pager.lower( ).endswith( '\\more.com' ): continue
                case _: pass
            break
    else: pager = ''

    if pager:

        # TODO? async
        def pager_executor( filename: str ) -> None:
            ''' Executes pager with file. '''
            run( ( pager, filename ), check = True ) # nosec B603

        return pager_executor

    # TODO? async
    def console_display( filename: str ) -> None:
        ''' Prints file to stdout and waits for ENTER key. '''
        with open( filename, 'r', encoding = 'utf-8' ) as stream:
            content = stream.read( )
        print( f"\n\n{content}\n\n" )
        if __.sys.stdin.isatty( ): input( "Press Enter to continue..." )

    _scribe.warning( "Could not find pager program for display." )
    return console_display


def display_content(
    content: str, *,
    suffix: str = '.txt',
    pager_discoverer: __.cabc.Callable[
        [ ], __.cabc.Callable[ [ str ], None ] ] = discover_pager,
) -> None:
    ''' Displays content via discovered pager. '''
    from .exceptions import PagerFailure
    pager = pager_discoverer( )
    import tempfile
    from pathlib import Path
    # Using delete = False to handle file cleanup manually. This ensures
    # the file handle is properly closed before the pager attempts to read it,
    # which is particularly important on Windows where open files cannot be
    # simultaneously accessed by other processes without a read share.
    with tempfile.NamedTemporaryFile(
        mode = 'w', suffix = suffix, delete = False, encoding = 'utf-8'
    ) as tmp:
        filename = tmp.name
        tmp.write( content )
    try: pager( filename )
    except Exception as exc: raise PagerFailure( cause = exc ) from exc
    finally:
        try: Path( filename ).unlink( )
        except Exception: # pylint: disable=broad-exception-caught
            _scribe.exception( f"Failed to cleanup {filename}" )
