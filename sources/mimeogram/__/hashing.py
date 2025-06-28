# Utility for deterministic hashing
import hashlib

def hash_mimeogram_parts(parts, message=None):
    m = hashlib.sha256()
    if message is not None:
        m.update(message.encode('utf-8'))
    for part in parts:
        m.update(str(part.location).encode('utf-8'))
        m.update(str(part.mimetype).encode('utf-8'))
        m.update(str(part.charset).encode('utf-8'))
        m.update(str(part.linesep.name).encode('utf-8'))
        m.update(str(part.content).encode('utf-8'))
    return m.hexdigest()
