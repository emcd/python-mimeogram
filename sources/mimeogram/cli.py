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

# TODO: Use BSD sysexits: os.EX_*.
# TODO: Factor out _scribe.exception / SystemExit pattern.


from __future__ import annotations

from . import __


# _scribe = __.produce_scribe( __name__ )


def create_parser( ) -> __.typx.Any:
    ''' Creates argument parser. '''
    import argparse
    from .apply import add_cli_subparser as add_apply_command_parser
    from .create import add_cli_subparser as add_create_command_parser
    parser = argparse.ArgumentParser(
        description = "Creates and applies mimeograms." )
    parser.add_argument(
        '-v',
        '--verbose',
        action = 'store_true',
        help = "Enables verbose logging" )
    subparsers = parser.add_subparsers(
        title = 'commands',
        dest = 'command',
        required = True )
    add_create_command_parser( subparsers )
    add_apply_command_parser( subparsers )
    return parser


async def main( args: __.typx.Optional[ __.cabc.Sequence[ str ] ] = None ):
    ''' CLI entry point. '''
    from .apply import Command as CommandApply, apply
    from .create import Command as CommandCreate, create
    parser = create_parser( )
    parsed_args = parser.parse_args( args )
    await _prepare( parsed_args.verbose )
    match parsed_args.command:
        case 'create':
            await create( CommandCreate(
                sources = parsed_args.sources,
                recursive = parsed_args.recursive,
                strict = parsed_args.strict,
                clip = parsed_args.clip,
                editor_message = parsed_args.editor_message
            ) )
        case 'apply':
            await apply( CommandApply(
                input = parsed_args.input,
                clip = parsed_args.clip,
                base_path = parsed_args.base_path,
                interactive = parsed_args.interactive,
                # force = parsed_args.force,
                dry_run = parsed_args.dry_run
            ) )
        case _:
            parser.print_help( )
            raise SystemExit( 1 )


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


async def _prepare( verbose: bool ) -> None:
    ''' Configures logging based on verbosity. '''
    # TODO: Move to preparation module.
    application = __.ApplicationInformation( )
    inscription = __.InscriptionControl(
        level = 'debug' if verbose else None, # type: ignore
        mode = __.InscriptionModes.Rich ) # type: ignore
    await __.prepare( # type: ignore
        application = application, inscription = inscription )
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


if '__main__' == __name__: __.asyncio.run( main( ) )
