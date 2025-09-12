import json
from pathlib import Path
import secrets

P = 1_000_000_007       # prima
G = 5                   # generator (primitive root) untuk p ini

PUB_FILE = Path("public_key.json")
PRV_FILE = Path("private_key.json")

# ---------- util kecil ----------
def inv_mod(a: int, p: int) -> int:
    # Karena p prima: a^(p-2) mod p
    return pow(a, p - 2, p)

def save_keys(pub: tuple[int,int,int], x: int) -> None:
    p, g, y = pub
    PUB_FILE.write_text(json.dumps({"p": p, "g": g, "y": y}), encoding="utf-8")
    PRV_FILE.write_text(json.dumps({"p": p, "x": x}), encoding="utf-8")

def load_public() -> tuple[int,int,int]:
    d = json.loads(PUB_FILE.read_text(encoding="utf-8"))
    return d["p"], d["g"], d["y"]

def load_private() -> tuple[int,int]:
    d = json.loads(PRV_FILE.read_text(encoding="utf-8"))
    return d["p"], d["x"]

def ensure_keys() -> None:
    if PUB_FILE.exists() and PRV_FILE.exists():
        return
    # keygen: pilih x acak, y = g^x mod p
    x = secrets.randbelow(P - 2) + 1       # 1..p-2
    y = pow(G, x, P)
    save_keys((P, G, y), x)
    print("Generated new keys.")
    print("Public (p,g,y):", (P, G, y))
    print("Private x saved to", PRV_FILE.name)

# ---------- inti ElGamal ----------
def encrypt_text(plain: str) -> str:
    """Enkripsi per byte b sebagai m=b+1 (hindari nol)."""
    p, g, y = load_public()
    out = []
    for b in plain.encode("utf-8"):
        m = b + 1
        k = secrets.randbelow(p - 2) + 1   # k acak setiap byte
        c1 = pow(g, k, p)
        s  = pow(y, k, p)                  # shared secret
        c2 = (m * s) % p
        out.append(f"{c1}:{c2}")
    return " ".join(out)

def decrypt_text(cipher: str) -> str:
    p, x = load_private()
    bytes_out = []
    for pair in cipher.strip().split():
        c1_s, c2_s = pair.split(":")
        c1, c2 = int(c1_s), int(c2_s)
        if c1 >= p or c2 >= p:
            raise ValueError("Ciphertext tidak cocok dengan modulus p pada kunci.")
        s = pow(c1, x, p)
        m = (c2 * inv_mod(s, p)) % p
        bytes_out.append((m - 1) & 0xFF)
    return bytes(bytes_out).decode("utf-8")

# ---------- CLI sederhana ----------
if __name__ == "__main__":
    ensure_keys()
    mode = input("Mode [e=encrypt / d=decrypt / n=newkey]: ").strip().lower()

    if mode.startswith("n"):
        # Buat ulang kunci (p,g tetap; x dan y baru)
        x = secrets.randbelow(P - 2) + 1
        y = pow(G, x, P)
        save_keys((P, G, y), x)
        print("New keys generated.")
        print("Public (p,g,y):", (P, G, y))
        print("Private x saved.")

    elif mode.startswith("e"):
        text = input("Plaintext: ")
        print("Ciphertext:", encrypt_text(text))

    elif mode.startswith("d"):
        ct = input("Ciphertext: ").strip()
        print("Plaintext:", decrypt_text(ct))

    else:
        print("Mode tidak dikenali.")
