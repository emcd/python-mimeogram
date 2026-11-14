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
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#  See the License for the specific language governing permissions and      #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Tests for prompt module. '''


import pytest

from . import PACKAGE_NAME, cache_import_module


def test_100_command_default_values( ):
    ''' Command initializes with correct default values. '''
    prompt = cache_import_module( f"{PACKAGE_NAME}.prompt" )

    cmd = prompt.Command( )
    assert cmd.clip is None


def test_110_command_configuration_edits( ):
    ''' Command generates correct configuration edits. '''
    prompt = cache_import_module( f"{PACKAGE_NAME}.prompt" )

    cmd = prompt.Command( clip = True )
    edits = cmd.provide_configuration_edits( )
    assert len( edits ) == 1
    assert edits[ 0 ].address == ( 'prompt', 'to-clipboard' )
    assert edits[ 0 ].value is True


def test_120_prompt_boolean_flag_forms( capsys ):
    ''' Real Tyro parser handles flag forms and rejects explicit values. '''
    prompt = cache_import_module( f"{PACKAGE_NAME}.prompt" )
    tyro = cache_import_module( 'tyro' )

    cmd = tyro.cli( prompt.Command, args = [ ] )
    assert cmd.clip is None
    cmd = tyro.cli( prompt.Command, args = [ '--to-clipboard' ] )
    assert cmd.clip is True
    cmd = tyro.cli( prompt.Command, args = [ '--no-clipboard' ] )
    assert cmd.clip is False
    for args in (
        [ '--clipboard', 'True' ],
        [ '--to-clipboard=False' ],
    ):
        with pytest.raises( SystemExit ) as exc_info:
            tyro.cli( prompt.Command, args = args )
        assert exc_info.value.code == 2
    with pytest.raises( SystemExit ) as exc_info:
        tyro.cli( prompt.Command, args = [ '--help' ] )
    assert exc_info.value.code == 0
    help_text = capsys.readouterr( ).out
    assert '--clipboard, --no-clipboard' in help_text
    edits = tyro.cli(
        prompt.Command, args = [ '--clipboard' ]
    ).provide_configuration_edits( )
    assert edits[ 0 ].address == ( 'prompt', 'to-clipboard' )
    assert edits[ 0 ].value is True


def test_130_prompt_documented_vector_and_edit_polarity( ):
    ''' Rewritten doc example parses; edits track absence/True/False. '''
    prompt = cache_import_module( f"{PACKAGE_NAME}.prompt" )
    tyro = cache_import_module( 'tyro' )

    tyro.cli( prompt.Command, args = [ '--no-clipboard' ] )
    cmd = tyro.cli( prompt.Command, args = [ ] )
    assert cmd.provide_configuration_edits( ) == ( )
    cmd = tyro.cli( prompt.Command, args = [ '--no-clipboard' ] )
    edits = {
        edit.address: edit.value
        for edit in cmd.provide_configuration_edits( ) }
    assert edits == { ( 'prompt', 'to-clipboard' ): False }
