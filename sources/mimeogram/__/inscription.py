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


''' Scribes for debugging and logging. '''


from . import imports as __


class Modes( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Possible modes for logging output. '''

    Null = 'null' # suppress library logs
    Pass = 'pass' # pass library logs to root logger # nosec
    Rich = 'rich' # print rich library logs to stderr


class Control(
    metaclass = __.ImmutableStandardDataclass,
    decorators = ( __.standard_dataclass, ),
):
    ''' Logging and debug printing behavior. '''

    mode: Modes = Modes.Null
    level: __.typx.Optional[ __.typx.Literal[
        'debug', 'info', 'warn', 'error', 'critical' # noqa: F821
    ] ] = None

    # TODO? Support capture file and stream choice.


def prepare( control: Control ) -> None:
    ''' Prepares various scribes in a sensible manner. '''
    prepare_scribe_icecream( control = control )
    prepare_scribe_logging( control = control )


def prepare_scribe_icecream( control: Control ) -> None:
    ''' Prepares Icecream debug printing. '''
    from os import environ
    match environ.get( '_DEVELOPMENT_MODE_', 'FALSE' ).upper( ):
        case '1' | 'ON' | 'T' | 'TRUE' | 'Y' | 'YES': pass
        case _:
            import builtins
            setattr( builtins, 'ic', _passthrough )
            return
    from icecream import ic, install
    nomargs: dict[ str, __.typx.Any ] = dict(
        includeContext = True, prefix = 'DEBUG    ' )
    match control.mode:
        case Modes.Null:
            ic.configureOutput( **nomargs )
            ic.disable( )
        case Modes.Pass:
            ic.configureOutput( **nomargs )
        case Modes.Rich: # pragma: no branch
            from rich.pretty import pretty_repr
            ic.configureOutput( argToStringFunction = pretty_repr, **nomargs )
    install( )


def prepare_scribe_logging( control: Control ) -> None:
    ''' Prepares standard Python logging. '''
    # https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
    import logging
    level_name = _discover_inscription_level_name( control )
    level = getattr( logging, level_name.upper( ) )
    scribe = __.produce_scribe( __.package_name )
    scribe.propagate = False # prevent double-logging
    scribe.setLevel( level )
    match control.mode:
        case Modes.Null:
            scribe.addHandler( logging.NullHandler( ) )
        case Modes.Pass:
            scribe.propagate = True
        case Modes.Rich: # pragma: no branch
            from rich.console import Console
            from rich.logging import RichHandler
            formatter = logging.Formatter( "%(name)s: %(message)s" )
            handler = RichHandler(
                console = Console( stderr = True ),
                rich_tracebacks = True,
                show_time = False )
            handler.setFormatter( formatter )
            scribe.addHandler( handler )
    scribe.debug( "Logging initialized." )


def _discover_inscription_level_name( control: Control ) -> str:
    if control.level is None:
        from os import environ
        for envvar_name_base in ( 'INSCRIPTION', 'LOG' ):
            envvar_name = (
                "{name}_{base}_LEVEL".format(
                    base = envvar_name_base,
                    name = __.package_name.upper( ) ) )
            if envvar_name not in environ: continue
            return environ[ envvar_name ]
        return 'INFO'
    return control.level


def _passthrough( *args: __.typx.Any ) -> __.cabc.Sequence[ __.typx.Any ]:
    return args
