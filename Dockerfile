
FROM balenalib/raspberrypi3-python:3.11.2-bookworm-build AS builder

WORKDIR /app

# Change the default apt sources to the archive repository
RUN sed -i 's/http:\/\/deb.debian.org/http:\/\/archive.debian.org/' /etc/apt/sources.list \
    && sed -i 's/http:\/\/security.debian.org/http:\/\/archive.debian.org/' /etc/apt/sources.list


# Add necessary build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libpython3-dev \
    libopenblas-dev \
    git



COPY requirements.txt .

# Upgrade pip first
RUN pip install --upgrade pip

#RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY detect.py .
COPY model/best.pt .
COPY dummy_image.jpg .

FROM balenalib/raspberrypi3-python:3.11.2-bookworm-run

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

COPY --from=builder /app/detect.py /app/detect.py
COPY --from=builder /app/model/best.pt /app/model/best.pt
COPY --from=builder /app/dummy_image.jpg /app/dummy_image.jpg

# Create necessary directories for your application's data or logs if it writes to them.
RUN mkdir -p /app/data /app/logs

CMD ["python", "detect.py","--test"]