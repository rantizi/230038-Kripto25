def _key_shifts(key: str):
    shifts = [ord(c.lower()) - 97 for c in key if c.isalpha()]
    if not shifts:
        raise ValueError("Key harus berisi minimal satu huruf (A-Z).")
    return shifts

def _vigenere(text: str, key: str, decrypt: bool = False) -> str:
    ks = _key_shifts(key)
    out, j = [], 0

    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            s = ks[j % len(ks)]
            if decrypt:
                s = -s
            # geser 0..25 lalu kembali ke huruf
            out.append(chr((ord(ch) - base + s) % 26 + base))
            j += 1
        else:
            out.append(ch)
    return ''.join(out)

def encrypt(plaintext: str, key: str) -> str:
    return _vigenere(plaintext, key, decrypt=False)

def decrypt(ciphertext: str, key: str) -> str:
    return _vigenere(ciphertext, key, decrypt=True)

if __name__ == "__main__":
    mode = input("Mode [e=encrypt / d=decrypt]: ").strip().lower()
    key = input("Key: ").strip()
    text = input("Teks: ")

    if mode in ("e", "encrypt"):
        print("Ciphertext:", encrypt(text, key))
    elif mode in ("d", "decrypt"):
        print("Plaintext:", decrypt(text, key))
    else:
        print("Mode tidak dikenali. Gunakan 'e' atau 'd'.")
