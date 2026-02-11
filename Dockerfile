# Use python 3.10 slim image
FROM python:3.10-slim

# Install system dependencies
# build-essential, cmake, git, python3-dev are required for compiling llama-cpp-python and TTS
# pkg-config and ALL libav*-dev are strictly required to compile PyAV (av)
# libsndfile1 is required for soundfile/torchaudio
# ffmpeg is required for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    cmake \
    git \
    python3-dev \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    libswscale-dev \
    libavfilter-dev \
    libavdevice-dev \
    libpostproc-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
# We use --prefer-binary to avoid compilation where a wheel is available
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
