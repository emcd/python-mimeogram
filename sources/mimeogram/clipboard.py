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


# Clipboard operations module.
#
# This module exists to work around a bug in pyperclip where calling
# subprocess.communicate() on xclip causes the process to hang indefinitely.
# xclip forks into the background to serve clipboard paste requests and never
# exits, but pyperclip waits for it to exit. The same bug exists in pyclip.
#
# See: https://github.com/asweigart/pyperclip/issues/247
#
# Our solution: Call xclip directly on Linux/X11 without waiting for exit.
# Fall back to pyperclip on other platforms (may still hang on some systems).


''' Clipboard operations. '''


import subprocess as _subprocess

from . import __


_scribe = __.produce_scribe( __name__ )


def copy_to_clipboard( text: str ) -> None:
    ''' Copies text to clipboard. '''
    # Try xclip first on Linux with X11
    if __.sys.platform == 'linux' and __.os.environ.get( 'DISPLAY' ):
        try:
            # Use xclip directly, don't wait for it to finish
            # xclip forks into background and stays running to serve pastes
            proc = _subprocess.Popen(
                [ 'xclip', '-selection', 'clipboard' ],  # noqa: S607
                stdin = _subprocess.PIPE,
                stdout = _subprocess.DEVNULL,
                stderr = _subprocess.DEVNULL,
                close_fds = True,
            )
        except FileNotFoundError:
            _scribe.debug( "xclip not found, falling back to pyperclip" )
        except Exception as exc:
            _scribe.warning(
                f"xclip failed ({exc}), falling back to pyperclip" )
        else:
            assert proc.stdin is not None  # noqa: S101
            proc.stdin.write( text.encode( 'utf-8' ) )
            proc.stdin.close( )
            # Don't call proc.wait() or proc.communicate() - let xclip fork
            _scribe.debug( "Copied to clipboard via xclip" )
            return
    # Fall back to pyperclip for other platforms or if xclip fails
    from pyperclip import copy
    try:
        copy( text )
    except Exception as exc:
        _scribe.error( f"Failed to copy to clipboard: {exc}" )
        raise
    _scribe.debug( "Copied to clipboard via pyperclip" )


def copy_from_clipboard( ) -> str:
    ''' Copies text from clipboard. '''
    from pyperclip import paste
    return paste( )
