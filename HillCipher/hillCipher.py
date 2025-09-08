import numpy as np
import sys

class HillCipher:
    """
    Kelas untuk enkripsi, dekripsi, dan pencarian kunci Hill Cipher.
    Menggunakan A=0, B=1, ..., Z=25.
    """

    def _matriks_ke_teks(self, matriks):
        """Mengubah matriks angka menjadi string."""
        return "".join([chr(int(c) + 65) for c in matriks.flatten()])

    def _teks_ke_matriks(self, teks, ukuran):
        """Mengubah string menjadi matriks angka, dengan padding jika perlu."""
        teks = "".join(filter(str.isalpha, teks.upper()))
        
        # Tambahkan padding 'X' jika panjang teks tidak kelipatan ukuran
        if len(teks) % ukuran != 0:
            teks += 'X' * (ukuran - len(teks) % ukuran)
            
        angka = [ord(c) - 65 for c in teks]
        return np.array(angka).reshape(-1, ukuran)

    def _invers_modular_matriks(self, matriks):
        """Menghitung invers modular dari sebuah matriks mod 26."""
        det = int(np.round(np.linalg.det(matriks)))
        det_inv = pow(det, -1, 26)
        
        invers = np.round(det_inv * np.linalg.det(matriks) * np.linalg.inv(matriks)).astype(int) % 26
        
        return invers

    def enkripsi(self, plaintext, kunci):
        """Enkripsi plaintext menggunakan Hill Cipher."""
        kunci_matriks = np.array(kunci)
        ukuran = kunci_matriks.shape[0]
        
        plaintext_matriks = self._teks_ke_matriks(plaintext, ukuran)
        
        hasil_matriks = (plaintext_matriks @ kunci_matriks) % 26
        
        return self._matriks_ke_teks(hasil_matriks)

    def dekripsi(self, ciphertext, kunci):
        """Dekripsi ciphertext menggunakan Hill Cipher."""
        kunci_matriks = np.array(kunci)
        
        try:
            invers_kunci = self._invers_modular_matriks(kunci_matriks)
        except (ValueError, np.linalg.LinAlgError):
            # Menangkap error jika determinan tidak memiliki invers modular
            return "Error: Matriks kunci tidak dapat di-invers. Dekripsi gagal."

        ciphertext_matriks = self._teks_ke_matriks(ciphertext, kunci_matriks.shape[0])
        hasil_matriks = (ciphertext_matriks @ invers_kunci) % 26
        
        return self._matriks_ke_teks(hasil_matriks)

# --- FUNGSI UNTUK INPUT PENGGUNA ---
def get_key_from_user():
    """Meminta dan memvalidasi input kunci dari pengguna."""
    while True:
        try:
            ukuran_str = input("Masukkan ukuran matriks kunci (misal: 2 untuk 2x2, 3 untuk 3x3): ")
            ukuran = int(ukuran_str)
            if ukuran <= 1:
                print("Ukuran harus lebih besar dari 1.")
                continue

            print(f"Masukkan elemen matriks kunci {ukuran}x{ukuran} (pisahkan dengan spasi per baris):")
            kunci = []
            for i in range(ukuran):
                baris_str = input(f"Baris {i+1}: ")
                baris = [int(x) for x in baris_str.split()]
                if len(baris) != ukuran:
                    print(f"Error: Harap masukkan {ukuran} angka untuk setiap baris.")
                    raise ValueError
                kunci.append(baris)
            
            # Coba hitung determinan untuk validasi awal
            np.linalg.det(np.array(kunci))
            return kunci
        except ValueError:
            print("Input tidak valid. Pastikan semua masukan adalah angka dan sesuai format.")
        except np.linalg.LinAlgError:
            print("Error: Matriks yang dimasukkan tidak valid (singular). Coba lagi.")

# --- PROGRAM UTAMA INTERAKTIF ---
if __name__ == "__main__":
    cipher = HillCipher()
    
    while True:
        print("\n--- Program Hill Cipher ---")
        print("1. Enkripsi Teks")
        print("2. Dekripsi Teks")
        print("3. Keluar")
        pilihan = input("Pilih operasi (1/2/3): ")

        if pilihan == '1':
            plaintext = input("Masukkan plaintext: ")
            kunci = get_key_from_user()
            ciphertext = cipher.enkripsi(plaintext, kunci)
            print("-" * 25)
            print(f"🔑 Kunci yang digunakan:\n{np.array(kunci)}")
            print(f"📄 Hasil Enkripsi: {ciphertext}")
            print("-" * 25)

        elif pilihan == '2':
            ciphertext = input("Masukkan ciphertext: ")
            kunci = get_key_from_user()
            plaintext = cipher.dekripsi(ciphertext, kunci)
            print("-" * 25)
            print(f"🔑 Kunci yang digunakan:\n{np.array(kunci)}")
            print(f"📄 Hasil Dekripsi: {plaintext}")
            print("-" * 25)

        elif pilihan == '3':
            print("Terima kasih! Program selesai.")
            sys.exit()

        else:
            print("Pilihan tidak valid. Harap masukkan 1, 2, atau 3.")