# Bike Sharing Data Analysis

Proyek akhir analisis data menggunakan **Bike Sharing Dataset** (Capital Bikeshare, Washington D.C., 2011–2012).

## Struktur Folder

```text
submission_bike_sharing/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── hour.csv
│   ├── day.csv
│   └── Readme.txt
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Pertanyaan Bisnis

1. Kapan rata-rata penyewaan per jam mencapai puncak pada hari kerja dibandingkan hari non-kerja selama 2011–2012?
2. Bagaimana perbedaan rata-rata penyewaan per jam berdasarkan kondisi cuaca selama 2011–2012?

## Analisis Lanjutan

Proyek menggunakan **manual grouping / binning** untuk membagi 24 jam menjadi lima periode operasional sehingga pola permintaan lebih mudah diterjemahkan menjadi jadwal rebalancing sepeda.

## Cara Menjalankan Notebook

Dari folder root submission, buka `notebook.ipynb` menggunakan Jupyter Notebook, JupyterLab, atau Google Colab. Pastikan folder `data/` berada pada lokasi relatif yang sama.

## Cara Menjalankan Dashboard

1. Buka terminal pada folder root submission.
2. Instal library:

```bash
pip install -r requirements.txt
```

3. Jalankan dashboard:

```bash
streamlit run dashboard/dashboard.py
```

4. Buka alamat yang ditampilkan Streamlit https://taopik-bike-sharing.streamlit.app/.
