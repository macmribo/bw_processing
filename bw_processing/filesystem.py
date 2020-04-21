# -*- coding: utf-8 -*-
import hashlib
import re
import unicodedata

re_slugify = re.compile(r"[^\w\s-]", re.UNICODE)
SUBSTITUTION_RE = re.compile(r"[^\w\-\.]")
MULTI_RE = re.compile(r"_{2,}")


def clean_datapackage_name(name):
    """Clean string ``name`` of characters not allowed in data package names.

    Replaces with underscores, and drops multiple underscores."""
    return re.sub(MULTI_RE, "_", re.sub(SUBSTITUTION_RE, "_", name).strip("_")).strip()


def safe_filename(string, add_hash=True):
    """Convert arbitrary strings to make them safe for filenames. Substitutes strange characters, and uses unicode normalization.

    if `add_hash`, appends hash of `string` to avoid name collisions.

    From http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python"""
    safe = re.sub(
        r"[-\s]+",
        "-",
        str(re_slugify.sub("", unicodedata.normalize("NFKD", str(string))).strip()),
    )
    if add_hash:
        if isinstance(string, str):
            string = string.encode("utf8")
        return safe + u"." + hashlib.md5(string).hexdigest()[:8]
    else:
        return safe


def md5(filepath, blocksize=65536):
    """Generate MD5 hash for file at `filepath`"""
    hasher = hashlib.md5()
    fo = open(filepath, "rb")
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()
