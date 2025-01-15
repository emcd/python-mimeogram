# Mimeogram Collaboration Guidelines

## Conversation Scope

When collaborating with LLMs on code changes using mimeograms:

1. Focus on one module or a small, related set of modules
2. Set clear boundaries for the changes before starting
3. Complete a mimeogram before moving to the next set of changes
4. Document any dependencies between changes

## Size Management

Mimeograms have practical size limits due to LLM token constraints:

1. Token Usage:
   - 1 character ≈ 0.3 tokens
   - Average Python line ≈ 40-60 characters (12-18 tokens)
   - Headers and boilerplate add ~300 tokens
   - Mimeogram packaging adds overhead

2. Recommended Limits:
   - Keep mimeograms under 300 lines of code
   - Target ~5000 tokens total including packaging
   - Consider splitting large changes across multiple conversations

## Change Strategy

For effective collaboration:

1. Plan refactoring in chunks that fit in one mimeogram
2. Complete standalone changes before interdependent ones
3. Document dependencies between changes
4. Consider package usability during partial updates

## Best Practices

1. Include complete context:
   - File headers
   - License information
   - Import statements
   - Required boilerplate

2. Maintain package stability:
   - Group related changes when possible
   - Update dependencies together
   - Keep the package importable during changes

3. Documentation:
   - Update relevant docs with code changes
   - Note any temporary limitations
   - Document planned follow-up changes

## Working with LLMs

1. Be explicit about:
   - Change scope and boundaries
   - Expected outcomes
   - Dependencies and constraints

2. Review changes before applying:
   - Check for missing context
   - Verify all dependencies are included
   - Ensure package remains functional

3. Plan for limitations:
   - Split large changes across conversations
   - Keep context focused and relevant
   - Document multi-step changes clearly