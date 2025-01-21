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


from . import __


_scribe = __.produce_scribe( __name__ )


def display_content(
    content: str,
    suffix: __.typx.Annotated[
        str, __.typx.Doc( "File extension for syntax highlighting" )
    ] = '.txt'
) -> None:
    ''' Displays content in system pager. '''
    from shutil import which
    pager = __.os.environ.get( 'PAGER', 'less' )
    # TODO: Platform-specific list.
    for pager_ in ( pager, 'less', 'more' ):
        if which( pager_ ):
            pager = pager_
            break
    else:
        print( content )
        input( "Press Enter to continue..." )
        return
    import tempfile
    import subprocess # nosec B404
    with tempfile.NamedTemporaryFile( mode='w', suffix=suffix ) as tmp:
        tmp.write( content )
        tmp.flush( )
        try: subprocess.run( [ pager, tmp.name ], check=True ) # nosec B603
        except subprocess.CalledProcessError:
            _scribe.exception( "Could not display content in pager." )
            # TODO: Raise appropriate error.
