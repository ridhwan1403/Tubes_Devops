# Gunakan base image Python
FROM python:3.9-slim

# Set direktori kerja
WORKDIR /app

# Salin file requirements dan instal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi
COPY . .

# Ekspos port
EXPOSE 5000

# Jalankan aplikasi
CMD ["python", "app.py"]
