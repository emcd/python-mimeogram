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


''' Tests for interactions module. '''
# pylint: disable=too-many-locals,unused-argument


import pytest

from . import PACKAGE_NAME, cache_import_module


def test_100_calculate_differences( ):
    ''' Difference calculation handles various content cases. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "" )

    # Empty both
    diff = interactions._calculate_differences( part, "", "" )
    assert not diff

    # Empty original
    diff = interactions._calculate_differences( part, "new content" )
    assert any( line.startswith( '+new content' ) for line in diff )

    # Changed content
    diff = interactions._calculate_differences(
        part, "new content", "old content" )
    assert any( line.startswith( '-old content' ) for line in diff )
    assert any( line.startswith( '+new content' ) for line in diff )


@pytest.mark.asyncio
async def test_200_interact_simple_apply( provide_tempdir ):
    ''' Apply resolution returned for unprotected content. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )

    async def mock_noop( *args ): pass
    def mock_always_apply( *args ): return 'a'
    def mock_noop_sync( *args ): pass
    async def mock_editor( *args ): return "test content"
    async def mock_selector( *args ): return "test content"

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "test content" )
    target = parts.Target(
        part = part,
        destination = provide_tempdir / "test.txt",
        protection = fsprotect.Status(
            active = False,
            reason = "",
            path = provide_tempdir / "test.txt" ) )

    interactor = interactions.GenericInteractor(
        prompter = mock_always_apply,
        cdisplayer = mock_noop,
        ddisplayer = mock_noop,
        editor = mock_editor,
        sselector = mock_selector,
        validator = mock_noop_sync )

    resolution, content = await interactions.interact( target, interactor )
    assert resolution == parts.Resolutions.Apply
    assert content == "test content"


@pytest.mark.asyncio
async def test_210_interact_simple_ignore( provide_tempdir ):
    ''' Ignore resolution returned for protected content. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )

    async def mock_noop( *args ): pass
    def mock_always_ignore( *args ): return 'i'
    def mock_noop_sync( *args ): pass
    async def mock_editor( *args ): return "test content"
    async def mock_selector( *args ): return "test content"

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "test content" )
    target = parts.Target(
        part = part,
        destination = provide_tempdir / "test.txt",
        protection = fsprotect.Status(
            active = True,
            reason = "",
            path = provide_tempdir / "test.txt" ) )

    interactor = interactions.GenericInteractor(
        prompter = mock_always_ignore,
        cdisplayer = mock_noop,
        ddisplayer = mock_noop,
        editor = mock_editor,
        sselector = mock_selector,
        validator = mock_noop_sync )

    resolution, content = await interactions.interact( target, interactor )
    assert resolution == parts.Resolutions.Ignore
    assert content == "test content"


@pytest.mark.asyncio
async def test_220_interact_edit_then_apply( provide_tempdir ):
    ''' Content editing followed by apply resolution. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )

    choices = iter( [ 'e', 'a' ] )
    async def mock_noop( *args ): pass
    def mock_sequential_choice( *args ): return next( choices )
    def mock_noop_sync( *args ): pass
    async def mock_editor( *args ): return "edited content"
    async def mock_selector( *args ): return "test content"

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "test content" )
    target = parts.Target(
        part = part,
        destination = provide_tempdir / "test.txt",
        protection = fsprotect.Status(
            active = False,
            reason = "",
            path = provide_tempdir / "test.txt" ) )

    interactor = interactions.GenericInteractor(
        prompter = mock_sequential_choice,
        cdisplayer = mock_noop,
        ddisplayer = mock_noop,
        editor = mock_editor,
        sselector = mock_selector,
        validator = mock_noop_sync )

    resolution, content = await interactions.interact( target, interactor )
    assert resolution == parts.Resolutions.Apply
    assert content == "edited content"


@pytest.mark.asyncio
async def test_230_interact_displays_content( provide_tempdir ):
    ''' Content display operations invoked appropriately. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )

    content_displayed = False
    differences_displayed = False
    choices = iter( [ 'v', 'd', 'i' ] )

    def mock_sequential_choice( *args ): return next( choices )
    def mock_noop_sync( *args ): pass
    async def mock_editor( *args ): return "test content"
    async def mock_selector( *args ): return "test content"

    async def mock_content_display( *args ):
        nonlocal content_displayed
        content_displayed = True

    async def mock_differences_display( *args ):
        nonlocal differences_displayed
        differences_displayed = True

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "test content" )
    target = parts.Target(
        part = part,
        destination = provide_tempdir / "test.txt",
        protection = fsprotect.Status(
            active = False,
            reason = "",
            path = provide_tempdir / "test.txt" ) )

    interactor = interactions.GenericInteractor(
        prompter = mock_sequential_choice,
        cdisplayer = mock_content_display,
        ddisplayer = mock_differences_display,
        editor = mock_editor,
        sselector = mock_selector,
        validator = mock_noop_sync )

    resolution, _ = await interactions.interact( target, interactor )
    assert resolution == parts.Resolutions.Ignore
    assert content_displayed
    assert differences_displayed


@pytest.mark.asyncio
async def test_240_interact_select_segments( provide_tempdir ):
    ''' Segment selection updates content. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )

    choices = iter( [ 's', 'a' ] )
    selector_called = False

    async def mock_noop( *args ): pass
    def mock_sequential_choice( *args ): return next( choices )
    def mock_noop_sync( *args ): pass
    async def mock_editor( *args ): return "test content"
    async def mock_selector( *args ):
        nonlocal selector_called
        selector_called = True
        return "selected content"

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "test content" )
    target = parts.Target(
        part = part,
        destination = provide_tempdir / "test.txt",
        protection = fsprotect.Status(
            active = False,
            reason = "",
            path = provide_tempdir / "test.txt" ) )

    interactor = interactions.GenericInteractor(
        prompter = mock_sequential_choice,
        cdisplayer = mock_noop,
        ddisplayer = mock_noop,
        editor = mock_editor,
        sselector = mock_selector,
        validator = mock_noop_sync )

    resolution, content = await interactions.interact( target, interactor )
    assert resolution == parts.Resolutions.Apply
    assert content == "selected content"
    assert selector_called


@pytest.mark.asyncio
async def test_300_interact_protected_flow( provide_tempdir ):
    ''' Protection removal enables edits. '''
    interactions = cache_import_module( f"{PACKAGE_NAME}.interactions" )
    parts = cache_import_module( f"{PACKAGE_NAME}.parts" )
    fsprotect = cache_import_module( f"{PACKAGE_NAME}.fsprotect" )

    choices = iter( [ 'e', 'p', 'e', 'a' ] )
    async def mock_noop( *args ): pass
    def mock_sequential_choice( *args ): return next( choices )
    def mock_noop_sync( *args ): pass
    async def mock_editor( *args ): return "edited content"
    async def mock_selector( *args ): return "test content"

    part = parts.Part(
        location = "test.txt",
        mimetype = "text/plain",
        charset = "utf-8",
        linesep = parts.LineSeparators.LF,
        content = "test content" )
    target = parts.Target(
        part = part,
        destination = provide_tempdir / "test.txt",
        protection = fsprotect.Status(
            active = True,
            reason = "",
            path = provide_tempdir / "test.txt" ) )

    interactor = interactions.GenericInteractor(
        prompter = mock_sequential_choice,
        cdisplayer = mock_noop,
        ddisplayer = mock_noop,
        editor = mock_editor,
        sselector = mock_selector,
        validator = mock_noop_sync )

    resolution, content = await interactions.interact( target, interactor )
    assert resolution == parts.Resolutions.Apply
    assert content == "edited content"
