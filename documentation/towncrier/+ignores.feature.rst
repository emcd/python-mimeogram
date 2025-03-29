Ignore macOS ``.DS_Store`` file, regardless of whether it is listed in
``.gitignore`` or whether there is a ``.gitignore`` when collecting files from
a directory.

Likewise, ignore ``.env`` when collecting files from a directory. (For
security reasons, as there may be secrets in it.)

One can still explicitly specify ignored files to include them in mimeograms.
Ignoring only applies to collecting files from directories, when directories
are given as arguments to ``mimeogram create``.
