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


''' Language model tokenizers. '''


from __future__ import annotations

import tiktoken as _tiktoken

from . import __


_scribe = __.produce_scribe( __name__ )



class Tokenizers( __.enum.Enum ):
    ''' Language model tokenizers. '''

    AnthropicApi =  'anthropic-api'
    Tiktoken =      'tiktoken'

    @classmethod
    async def produce(
        selfclass, name: str, variant: __.Absential[ str ] = __.absent
    ) -> Tokenizer:
        ''' Produces tokenizer from name and optional variant. '''
        tokenizer = selfclass( name )
        match tokenizer:
            case Tokenizers.AnthropicApi:
                raise NotImplementedError( "Not implemented yet. Sorry." )
            case Tokenizers.Tiktoken:
                return await Tiktoken.from_variant( name = variant )


class Tokenizer(
    __.typx.Protocol,
    metaclass = __.ImmutableStandardProtocolDataclass,
    decorators = ( __.standard_dataclass, __.typx.runtime_checkable, ),
):
    ''' Language model tokenizer. '''

    @classmethod
    @__.abc.abstractmethod
    async def from_variant(
        selfclass, name: __.Absential[ str ] = __.absent
    ) -> __.typx.Self:
        ''' Produces instance from name of variant. '''

    @__.abc.abstractmethod
    async def count( self, text: str ) -> int:
        ''' Counts number of tokens in text. '''
        raise NotImplementedError


# TODO: Implement 'AnthropicApi' tokenizer.


class Tiktoken(
    Tokenizer, decorators = ( __.standard_dataclass, )
):
    ''' Tokenization via 'tiktoken' package. '''

    codec: _tiktoken.Encoding

    @classmethod
    async def from_variant(
        selfclass, name: __.Absential[ str ] = __.absent
    ) -> __.typx.Self:
        if __.is_absent( name ): name = 'cl100k_base'
        from tiktoken import get_encoding
        try: codec = get_encoding( name )
        except ValueError as exc:
            from .exceptions import TokenizerVariantInvalidity
            raise TokenizerVariantInvalidity( 'tiktoken', name ) from exc
        return selfclass( codec = codec )

    async def count( self, text: str ) -> int:
        return len( self.codec.encode( text ) )
