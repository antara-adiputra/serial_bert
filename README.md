## **Serial BER Test**
Aplikasi ini digunakan untuk menghitung nilai **_Bit Error Rate_ (BER)** pada sebuah link komunikasi serial (**RS232**) untuk menguji kualitas link komunikasi. Pengujian BER Test tidak dapat dilakukan secara langsung pada link komunikasi yg sudah terhubung dengan peralatan lain pada sisi ujungnya, melainkan hanya dapat dilakukan ketika sisi ujung komunikasi serial telah **ter-_loop_** (Pin Tx-Rx dijumper). Dari hasil nilai BER Test, user dapat mengetahui nilai persentase **_Confidence Level_** terhadap standar nilai BER yang telah ditetapkan apabila diimplementasikan langsung pada link komunikasi yang diuji.

`Module : Python3.10+, PySerial, nicegui`

#### Feature
   1. Menguji **Serial COM** maupun **Serial Over TCP/IP**
   1. Menghitung BER
   1. Menghitung Confidence Level

#### Prasyarat Penggunaan Aplikasi
- USB to Serial
- Kabel serial RS232 sesuai kebutuhan
- Kabel LAN (mode Raw Socket)

#### Parameter
   1. Parameter Serial
      + **Serial COM** : Mode port serial murni.
         - **Serial Port** : Port serial yang digunakan pada PC/Laptop (ex. COM1 pada Windows, /dev/ttyUSB0 pada Linux). Pastikan driver USB to Serial sudah terinstall pada PC/Laptop.
         - **Flow Control** : Flow control dalam transmisi sinyal. (Tidak digunakan dalam uji ini)
         - **Baud Rate** : Nilai baudrate. (default 9600)
         - **Data Bit** : Jumlah data bit. (default 8)
         - **Parity** : Jenis parity bit **N**one, **E**ven, atau **O**dd. (default **N**)
         - **Stop Bit** : Jumlah stop bit. (default 1)
      + **Raw Socket** : Mode serial via koneksi TCP.
         - **Remote IP** : IP address target.
         - **Port** : TCP port.
   1. Parameter Test
      + **Data Timeout** : Waktu timeout satu set data (bisa terdiri dari beberapa kali transmisi frame) diterima. (default 3s)
      + **Frame Timeout** : Waktu timeout port serial dalam satu kali penerimaan transmisi frame. (default 1.2s)
      + **Max Frame Length** : Panjang maksimal frame dalam sekali transmisi data. (default 255, min=1, max=1024)
      + **Desired BER** : Nila standar BER yang ingin dicapai. (default 10<sup>-6</sup>)
      + **Test Duration** : Durasi test _loopback_ serial. (default 10s)
      + **Frame Transmission** : Panjang frame transmisi data konstan (**Fixed Length**) atau bervariasi (**Diversed Length**) berdasarkan panjang maksimum frame.
   1. Hasil Test
      + **Frames Transmitted** : Jumlah frame yang dikirim.
      + **Frames Received** : Jumlah frame yang diterima.
      + **Tx/Rx Counter** : Jumlah kali transmisi frame selama durasi test.
      + **Error Frames** : Jumlah frame error selama durasi test.
      + **Error Bits** : Jumlah bit error selama durasi test.
      + **Bit Transmitted** : Jumlah bit yang dikirim selama durasi test.
      + **Bit Error Rate** : Output nilai BER dengan rumus **"Error Bits / Bit Transmitted"**. Bila jumlah bit error adalah 0, maka nilai BER dihitung dengan **"1 / (Bit Transmitted + 1)"**.
      + **Confidence Level** : Persentase "keyakinan" bahwa nilai BER saat kondisi sesungguhnya (komunikasi serial antar ujung peralatan) akan lebih rendah dari nilai standar BER yang ditetapkan. Perhitungan ini menggunakan rumus [distribusi Poisson](https://www.sitime.com/ber-confidence-level-calculator).
      + **Avg. Propagation Time** : Rata-rata waktu propagasi dari data dikirim hingga diterima kembali. (`t`<sub>`TxRx`</sub> + `t`<sub>`internal`</sub>)
      + **Avg. Link Latency** : Rata-rata waktu delay yang timbul disisi link komunikasi serial.

#### Metode Test
   1. **Simple Loop Test** : Test sederhana dengan mengirim karakter kemudian membandingkan dengan karakter yang diterima untuk mengetahui bahwa ujung link komunikasi serial telah di-_loop_.
   1. **Run Test** : Test dengan mengirim-menerima data serial dalam durasi tertentu sesuai dengan parameter-parameter yang telah dikonfigurasi.

#### Contributor
Agus Antara [(@antara-adiputra)](https://github.com/antara-adiputra/)