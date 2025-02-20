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


''' Command-line interface. '''


from __future__ import annotations

from . import __
from . import apply as _apply
from . import create as _create
from . import interfaces as _interfaces
from . import prompt as _prompt


_scribe = __.produce_scribe( __name__ )


class VersionCommand(
    _interfaces.CliCommand,
    decorators = ( __.standard_dataclass, __.standard_tyro_class ),
):
    ''' Prints version information. '''

    async def __call__( self, auxdata: __.Globals ) -> None:
        ''' Executes command to print version information. '''
        from . import __version__ # pylint: disable=cyclic-import
        print( f"{__package__} {__version__}" )
        raise SystemExit( 0 )

    def provide_configuration_edits( self ) -> __.DictionaryEdits:
        ''' Provides edits against configuration from options. '''
        return ( )


class Cli(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, __.simple_tyro_class ),
):
    ''' Mimeogram: hierarchical data exchange between humans and LLMs. '''

    application: __.ApplicationInformation
    configfile: __.typx.Optional[ str ] = None
    # display: ConsoleDisplay
    inscription: __.InscriptionControl = (
        __.InscriptionControl( mode = __.InscriptionModes.Rich ) )
    command: __.typx.Union[
        __.typx.Annotated[
            _create.Command,
            __.tyro.conf.subcommand( # pyright: ignore
                'create', prefix_name = False ),
        ],
        __.typx.Annotated[
            _apply.Command,
            __.tyro.conf.subcommand( # pyright: ignore
                'apply', prefix_name = False ),
        ],
        __.typx.Annotated[
            _prompt.Command,
            __.tyro.conf.subcommand( # pyright: ignore
                'provide-prompt', prefix_name = False ),
        ],
        __.typx.Annotated[
            VersionCommand,
            __.tyro.conf.subcommand( # pyright: ignore
                'version', prefix_name = False ),
        ],
    ]

    async def __call__( self ):
        ''' Invokes command after library preparation. '''
        nomargs = self.prepare_invocation_args( )
        async with __.ExitsAsync( ) as exits:
            auxdata = await _prepare( exits = exits, **nomargs )
            await self.command( auxdata = auxdata )
            # await self.command( auxdata = auxdata, display = self.display )

    def prepare_invocation_args(
        self,
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Prepares arguments for initial configuration. '''
        configedits: __.DictionaryEdits = (
            self.command.provide_configuration_edits( ) )
        args: dict[ str, __.typx.Any ] = dict(
            application = self.application,
            configedits = configedits,
            environment = True,
            inscription = self.inscription,
        )
        if self.configfile: args[ 'configfile' ] = self.configfile
        return args


def execute( ):
    ''' Entrypoint for CLI execution. '''
    from asyncio import run
    config = (
        __.tyro.conf.EnumChoicesFromValues,
        __.tyro.conf.HelptextFromCommentsOff,
    )
    # default = Cli(
    #     application = _application.Information( ),
    #     display = ConsoleDisplay( ),
    #     inscription = _inscription.Control( mode = _inscription.Modes.Rich ),
    #     command = InspectCommand( ),
    # )
    try: run( __.tyro.cli( Cli, config = config )( ) )
    except SystemExit: raise
    except BaseException:
        _scribe.exception(
            "Program terminated from uncaught exception. "
            "Please file a bug report." )
        raise SystemExit( 1 ) from None


def _discover_inscription_level_name(
    application: __.ApplicationInformation,
    control: __.InscriptionControl,
) -> str:
    if control.level is None:
        from os import environ
        for envvar_name_base in ( 'INSCRIPTION', 'LOG' ):
            envvar_name = (
                "{name}_{base}_LEVEL".format(
                    base = envvar_name_base,
                    name = application.name.upper( ) ) )
            if envvar_name not in environ: continue
            return environ[ envvar_name ]
        return 'INFO'
    return control.level


async def _prepare(
    application: __.ApplicationInformation,
    configedits: __.DictionaryEdits,
    environment: bool,
    exits: __.ExitsAsync,
    inscription: __.InscriptionControl,
) -> __.Globals:
    ''' Configures logging based on verbosity. '''
    auxdata = await __.prepare(
        application = application,
        configedits = configedits,
        environment = environment,
        exits = exits,
        inscription = inscription )
    _prepare_scribes( application, inscription )
    return auxdata


def _prepare_scribes(
    application: __.ApplicationInformation,
    inscription: __.InscriptionControl,
) -> None:
    import logging
    from rich.console import Console
    from rich.logging import RichHandler
    level_name = _discover_inscription_level_name( application, inscription )
    level = getattr( logging, level_name.upper( ) )
    handler = RichHandler(
        console = Console( stderr = True ),
        rich_tracebacks = True,
        show_time = False )
    logging.basicConfig(
        format = '%(name)s: %(message)s',
        level = level,
        handlers = [ handler ] )
    logging.captureWarnings( True )
