#! /usr/bin/python3
# by pts@fazekas.hu at Thu May 24 18:44:15 CEST 2018
"""Pure Python 3 implementation of the ChaCha20 stream cipher.
https://github.com/pts/chacha20

It works with Python 3.5 (and probably also earler Python 3.x).

Based on https://gist.github.com/cathalgarvey/0ce7dbae2aa9e3984adc
Based on Numpy implementation: https://gist.github.com/chiiph/6855750
Based on http://cr.yp.to/chacha.html

More info about ChaCha20: https://en.wikipedia.org/wiki/Salsa20
"""

import binascii
from datetime import datetime
import struct
import random
import string


def decryptToken(cypherHex, noncesuffix, settings, returnAsUTF8=False, inputAsUTF8=False):
    """ encryt decrypt from hex to hex 
    
    if returnAsUTF8 is true, then return as utf8
    """
    # ChaCha20 Decode
    assert settings.CHACHA20_NONCE_BASE
    assert settings.CHACHA20_SECRET_KEY

    try:
        if inputAsUTF8:
            tokeninput = cypherHex.encode("utf-8")
        else:
            tokeninput = binascii.unhexlify(cypherHex)
        noncestr = '%s%s' % (settings.CHACHA20_NONCE_BASE, noncesuffix)
        nonce8 = binascii.unhexlify(noncestr)
        privatestr = settings.CHACHA20_SECRET_KEY
        private = binascii.unhexlify(privatestr)
        original = chacha20_encrypt(tokeninput, private, nonce8)
        if returnAsUTF8:
            return original.decode("utf-8")
        return binascii.hexlify(original).decode("utf-8")
    except binascii.Error:
        raise ValueError('Invalid Token. %s %s' % (cypherHex, noncesuffix))


def set_new_token(username):
    now = datetime.now()
    assert username
    timestamp = round(datetime.timestamp(now))
    tokenpart = ''.join(random.choices(string.ascii_uppercase + string.digits, k=35)) 
    return ('%s:%s:%s' % (username, tokenpart, timestamp))


def validtoken(token, settings):
    if not token:
        return False

    tokencomponents = token.split(':')
    if not tokencomponents or len(tokencomponents) != 3:
        return False
    
    username, tokenpart, datetime_ = tokencomponents
    if not tokenpart or not datetime_ or not username:
        return False
    dt_object = datetime.fromtimestamp(int(datetime_))
    assert dt_object
    delta = dt_object - datetime.now()
    if delta.seconds/60/60 > settings.AUTH_TOKEN_HOURS_UNTIL_EXPIRATION:
        return False
    
    return True


def yield_chacha20_xor_stream(key, iv, position=0):
  """Generate the xor stream with the ChaCha20 cipher."""
  if not isinstance(position, int):
    raise TypeError
  if position & ~0xffffffff:
    raise ValueError('Position is not uint32.')
  if not isinstance(key, bytes):
    raise TypeError
  if not isinstance(iv, bytes):
    raise TypeError
  if len(key) != 32:
    raise ValueError
  if len(iv) != 8:
    raise ValueError

  def rotate(v, c):
    return ((v << c) & 0xffffffff) | v >> (32 - c)

  def quarter_round(x, a, b, c, d):
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = rotate(x[d] ^ x[a], 16)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = rotate(x[b] ^ x[c], 12)
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = rotate(x[d] ^ x[a], 8)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = rotate(x[b] ^ x[c], 7)

  ctx = [0] * 16
  ctx[:4] = (1634760805, 857760878, 2036477234, 1797285236)
  ctx[4 : 12] = struct.unpack('<8L', key)
  ctx[12] = ctx[13] = position
  ctx[14 : 16] = struct.unpack('<LL', iv)
  while 1:
    x = list(ctx)
    for i in range(10):
      quarter_round(x, 0, 4,  8, 12)
      quarter_round(x, 1, 5,  9, 13)
      quarter_round(x, 2, 6, 10, 14)
      quarter_round(x, 3, 7, 11, 15)
      quarter_round(x, 0, 5, 10, 15)
      quarter_round(x, 1, 6, 11, 12)
      quarter_round(x, 2, 7,  8, 13)
      quarter_round(x, 3, 4,  9, 14)
    for c in struct.pack('<16L', *(
        (x[i] + ctx[i]) & 0xffffffff for i in range(16))):
      yield c
    ctx[12] = (ctx[12] + 1) & 0xffffffff
    if ctx[12] == 0:
      ctx[13] = (ctx[13] + 1) & 0xffffffff


def chacha20_encrypt(data, key, iv=None, position=0):
  """Encrypt (or decrypt) with the ChaCha20 cipher."""
  if not isinstance(data, bytes):
    raise TypeError
  if iv is None:
    iv = b'\0' * 8
  if isinstance(key, bytes):
    if not key:
      raise ValueError('Key is empty.')
    if len(key) < 32:
      # TODO(pts): Do key derivation with PBKDF2 or something similar.
      key = (key * (32 // len(key) + 1))[:32]
    if len(key) > 32:
      raise ValueError('Key too long.')

  return bytes(a ^ b for a, b in
      zip(data, yield_chacha20_xor_stream(key, iv, position)))
