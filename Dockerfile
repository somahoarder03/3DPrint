
FROM balenalib/raspberrypi3-python:3.11.2-bullseye-build AS builder

WORKDIR /app

# Change the default apt sources to the archive repository
RUN sed -i 's/http:\/\/deb.debian.org/http:\/\/archive.debian.org/' /etc/apt/sources.list \
    && sed -i 's/http:\/\/security.debian.org/http:\/\/archive.debian.org/' /etc/apt/sources.list


# Add necessary build dependencies




COPY requirements.txt .

RUN python -m ensurepip --upgrade

# Upgrade pip first
RUN python -m pip install --upgrade pip

#RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY detect.py .
COPY model/best.pt .
COPY dummy_image.jpg .

FROM balenalib/raspberrypi3-python:3.11.2-bullseye-run

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

COPY --from=builder /app/detect.py /app/detect.py
COPY --from=builder /app/model/best.pt /app/model/best.pt
COPY --from=builder /app/dummy_image.jpg /app/dummy_image.jpg

# Create necessary directories for your application's data or logs if it writes to them.
RUN mkdir -p /app/data /app/logs

CMD ["python", "detect.py","--test"]