CLI: Remove explicit-value spellings for boolean flags. Optional booleans
now accept only bare ``--flag`` (sets ``True``) and ``--no-flag`` (sets
``False``); omitted flags preserve the ``None`` default for configuration
layering. The old ``--flag True``, ``--flag=True``, and ``--flag=False``
forms are rejected with a usage error. Plain ``bool`` options (``--edit``,
``--prepend-prompt``) are unchanged.
