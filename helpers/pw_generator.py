import secrets
import string

_letters = string.ascii_letters
_digits = string.digits
_special_chars = string.punctuation

_alphabet = _letters + _digits + _special_chars

PASSWORD_LENGTH = 10


def generate_password(length=PASSWORD_LENGTH):
    pw = ''
    for i in range(length):
        pw += ''.join(secrets.choice(_alphabet))
    
    return pw
