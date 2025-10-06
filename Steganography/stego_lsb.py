from PIL import Image
import random, struct
from hashlib import sha256
from pathlib import Path

# Util 
def derive_seed(passphrase: str) -> int:
    # Ubah passphrase jadi seed stabil (64-bit dari SHA-256)
    return int.from_bytes(sha256(passphrase.encode()).digest()[:8], "big")

def shuffled_positions(w: int, h: int, seed: int):
    idx = list(range(w * h))
    rnd = random.Random(seed)
    rnd.shuffle(idx)
    return idx  # urutan piksel acak

def bits_from_bytes(data: bytes):
    for b in data:
        for i in range(8):
            yield (b >> (7 - i)) & 1

def bytes_from_bits(bits):
    out = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for j in range(8):
            b = (b << 1) | bits[i + j]
        out.append(b)
    return bytes(out)

def capacity_bytes(w: int, h: int) -> int:
    # Tiap piksel punya 3 kanal (R,G,B) => 3 bit per piksel (pakai 1 LSB/kanal)
    return (w * h * 3) // 8

# Encode
def encode_lsb_keyed(cover_path: str, out_path: str, message: str, passphrase: str):
    img = Image.open(cover_path).convert("RGB")
    w, h = img.size
    px = img.load()

    payload = message.encode("utf-8")
    header = struct.pack(">I", len(payload))  # 4 byte big-endian untuk panjang
    stream = list(bits_from_bytes(header + payload))

    cap = capacity_bytes(w, h)
    need_bytes = len(stream) // 8 + (1 if len(stream) % 8 else 0)
    if need_bytes > cap:
        raise ValueError(
            f"Pesan terlalu besar. Kapasitas ≈ {cap} byte, butuh ≈ {need_bytes} byte."
        )

    pos = shuffled_positions(w, h, derive_seed(passphrase))
    k = 0  # index bit

    for n in range(len(pos)):
        if k >= len(stream):
            break
        x = pos[n] % w
        y = pos[n] // w
        r, g, b = px[x, y]

        if k < len(stream):
            r = (r & ~1) | stream[k]; k += 1
        if k < len(stream):
            g = (g & ~1) | stream[k]; k += 1
        if k < len(stream):
            b = (b & ~1) | stream[k]; k += 1

        px[x, y] = (r, g, b)

    # Simpan sebagai PNG/BMP
    out_ext = Path(out_path).suffix.lower()
    if out_ext not in {".png", ".bmp"}:
        out_path = str(Path(out_path).with_suffix(".png"))
    img.save(out_path)
    return out_path

# Decode
def bit_generator(img: Image.Image, pos_list):
    w, h = img.size
    px = img.load()
    for n in range(len(pos_list)):
        x = pos_list[n] % w
        y = pos_list[n] // w
        r, g, b = px[x, y]
        yield r & 1
        yield g & 1
        yield b & 1

def decode_lsb_keyed(stego_path: str, passphrase: str) -> str:
    img = Image.open(stego_path).convert("RGB")
    w, h = img.size
    cap = capacity_bytes(w, h)
    pos = shuffled_positions(w, h, derive_seed(passphrase))
    gen = bit_generator(img, pos)

    # Ambil 32 bit pertama untuk panjang
    header_bits = [next(gen) for _ in range(32)]
    L = 0
    for b in header_bits:
        L = (L << 1) | b

    # Validasi panjang agar tidak bogus saat kunci salah
    max_payload = cap - 4  # sisakan 4 byte header
    if L < 0 or L > max_payload:
        raise ValueError(
            "Kunci salah atau tidak ada pesan tertanam (panjang tidak valid)."
        )

    # Baca L byte berikutnya
    msg_bits = [next(gen) for _ in range(L * 8)]
    msg = bytes_from_bits(msg_bits).decode("utf-8", errors="replace")
    return msg

# CLI Menu
def main():
    while True:
        print("\n=== Steganografi LSB (acak + stego-key) ===")
        print("1) Encode (sembunyikan teks)")
        print("2) Decode (ambil teks)")
        print("3) Keluar")
        choice = input("Pilih [1/2/3]: ").strip()

        if choice == "1":
            cover = input("Path cover image (PNG/BMP), contoh cover.png: ").strip()
            if not Path(cover).exists():
                print("File cover tidak ditemukan.")
                continue
            message = input("Ketik pesan yang akan disembunyikan: ")
            key = input("Passphrase (kunci): ")
            outp = input("Nama file output (mis. stego.png): ").strip() or "stego.png"
            try:
                out_file = encode_lsb_keyed(cover, outp, message, key)
                print(f"Berhasil. Hasil disimpan ke: {out_file}")
            except Exception as e:
                print(f"Gagal encode: {e}")

        elif choice == "2":
            stego = input("Path stego image (PNG/BMP), contoh stego.png: ").strip()
            if not Path(stego).exists():
                print("File stego tidak ditemukan.")
                continue
            key = input("Passphrase (kunci): ")
            try:
                msg = decode_lsb_keyed(stego, key)
                print("\n--- Pesan Tersembunyi ---")
                print(msg)
                print("-------------------------")
            except Exception as e:
                print(f"Gagal decode: {e}")

        elif choice == "3":
            print("Selesai.")
            break
        else:
            print("Pilihan tidak dikenal.")

if __name__ == "__main__":
    main()
