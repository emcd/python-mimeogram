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

class Pager:
    """Interface to system pager."""

    @staticmethod
    def display_content(
        content: str,
        suffix: __.typx.Annotated[
            str, __.typx.Doc("File extension for syntax highlighting")
        ] = '.txt'
    ) -> None:
        """Display content in system pager."""
        import tempfile
        import subprocess

        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix) as tmp:
            tmp.write(content)
            tmp.flush()

            pager = __.os.environ.get('PAGER', 'less')
            if not pager:
                pager = 'less'

            try:
                subprocess.run([pager, tmp.name], check=True)
            except subprocess.CalledProcessError:
                if pager == 'less':
                    subprocess.run(['more', tmp.name], check=True)
            except FileNotFoundError:
                # If no pager available, just print
                print(content)
                input("Press Enter to continue...")
