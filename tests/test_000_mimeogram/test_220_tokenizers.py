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

''' Tests for tokenizers module. '''

import pytest

from . import PACKAGE_NAME, cache_import_module


try:  # pragma: no cover - skip if tiktoken resources unavailable
    import tiktoken as _tiktoken

    _tiktoken.get_encoding( "cl100k_base" )
except Exception:  # best-effort check
    pytest.skip( "tiktoken resources unavailable", allow_module_level = True )

@pytest.mark.asyncio
async def test_100_produce_tokenizer_default_tiktoken( ):
    ''' Default Tiktoken tokenizer uses expected variant. '''
    tokenizers = cache_import_module( f"{PACKAGE_NAME}.tokenizers" )
    tokenizer = await tokenizers.Tokenizers.produce( "tiktoken" )
    assert isinstance( tokenizer, tokenizers.Tiktoken )
    assert tokenizer.codec.name == "cl100k_base"

@pytest.mark.asyncio
async def test_110_produce_tokenizer_tiktoken_variant( ):
    ''' Tiktoken tokenizer applies specified variant. '''
    tokenizers = cache_import_module( f"{PACKAGE_NAME}.tokenizers" )
    tokenizer = await tokenizers.Tokenizers.produce(
        "tiktoken", variant = "o200k_base" )
    assert isinstance( tokenizer, tokenizers.Tiktoken )
    assert tokenizer.codec.name == "o200k_base"

@pytest.mark.asyncio
async def test_120_validate_tokenizer_tiktoken_invalid_variant( ):
    ''' Invalid variant for Tiktoken raises TokenizerVariantInvalidity. '''
    tokenizers = cache_import_module( f"{PACKAGE_NAME}.tokenizers" )
    exceptions = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
    with pytest.raises( exceptions.TokenizerVariantInvalidity ) as exc_info:
        await tokenizers.Tokenizers.produce(
            "tiktoken", variant = "invalid_variant" )
    assert "invalid_variant" in str( exc_info.value )
    assert "tiktoken" in str( exc_info.value )

@pytest.mark.asyncio
async def test_130_produce_tokenizer_anthropic_not_implemented( ):
    ''' AnthropicApi tokenizer emits NotImplementedError. '''
    tokenizers = cache_import_module( f"{PACKAGE_NAME}.tokenizers" )
    with pytest.raises( NotImplementedError ) as exc_info:
        await tokenizers.Tokenizers.produce( "anthropic-api" )
    assert "Not implemented yet" in str( exc_info.value )

@pytest.mark.asyncio
async def test_140_calculate_token_count_tiktoken( ):
    ''' Tiktoken counts tokens in text as nonzero integer. '''
    tokenizers = cache_import_module( f"{PACKAGE_NAME}.tokenizers" )
    tokenizer = await tokenizers.Tokenizers.produce( "tiktoken" )
    text = "Hello, world!"
    count = await tokenizer.count( text )
    assert count > 0
    assert isinstance( count, int )

@pytest.mark.asyncio
async def test_150_calculate_token_count_tiktoken_empty_text( ):
    ''' Tiktoken assigns zero tokens to empty text. '''
    tokenizers = cache_import_module( f"{PACKAGE_NAME}.tokenizers" )
    tokenizer = await tokenizers.Tokenizers.produce( "tiktoken" )
    count = await tokenizer.count( "" )
    assert count == 0
