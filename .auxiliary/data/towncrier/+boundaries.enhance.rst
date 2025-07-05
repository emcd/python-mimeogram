Add deterministic boundary option for reproducible mimeogram output. When
enabled via ``--deterministic-boundary`` CLI flag or ``deterministic-boundary``
configuration setting, boundaries are generated from content hashes instead of
random UUIDs, making output diff-friendly for version control workflows.
(Feature request from @developingjames.)