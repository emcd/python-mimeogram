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

def display_content(
    content: str,
    suffix: __.typx.Annotated[
        str, __.typx.Doc( "File extension for syntax highlighting" )
    ] = '.txt'
) -> None:
    ''' Displays content in system pager. '''
    import tempfile
    import subprocess # nosec: b404
    with tempfile.NamedTemporaryFile( mode='w', suffix=suffix ) as tmp:
        tmp.write( content )
        tmp.flush( )
        pager = __.os.environ.get( 'PAGER', 'less' )
        try: subprocess.run( [ pager, tmp.name ], check=True ) # nosec: b603
        except subprocess.CalledProcessError:
            if pager == 'less':
                subprocess.run(
                    [ 'more', tmp.name ], check=True ) # nosec: b603,b607
        except FileNotFoundError:
            print(content)
            input( "Press Enter to continue..." )
