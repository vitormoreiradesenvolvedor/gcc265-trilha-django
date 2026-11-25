import hashlib
import hmac

from django.contrib.auth.hashers import PBKDF2PasswordHasher


def _pbkdf2_sha256(senha, sal, iteracoes):
    """PBKDF2-HMAC-SHA256 com um bloco de 32 bytes (RFC 8018), em Python puro.
    O hashlib do Pyodide não traz pbkdf2_hmac, que depende do OpenSSL."""
    prf = hmac.new(senha, digestmod=hashlib.sha256)

    def rodada(dados):
        h = prf.copy()
        h.update(dados)
        return h.digest()

    u = rodada(sal + b"\x00\x00\x00\x01")
    resultado = int.from_bytes(u, "big")
    for _ in range(iteracoes - 1):
        u = rodada(u)
        resultado ^= int.from_bytes(u, "big")
    return resultado.to_bytes(32, "big")


class PBKDF2Navegador(PBKDF2PasswordHasher):
    """Usado só na versão do navegador (settings_navegador). Ver o comentário lá."""

    algorithm = "pbkdf2_sha256_navegador"
    iterations = 5_000

    def encode(self, password, salt, iterations=None):
        import base64

        self._check_encode_args(password, salt)
        iterations = iterations or self.iterations
        chave = _pbkdf2_sha256(password.encode(), salt.encode(), iterations)
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, base64.b64encode(chave).decode("ascii").strip())
