# Menggunakan image Python ringan
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Copy semua file dari folder lokal ke container
COPY . .

# Install dependencies (jika ada requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

# Perintah default saat container dijalankan
CMD ["python", "-c", "print('Hello from Docker! FAHRIL PROJECT is ready.')"]