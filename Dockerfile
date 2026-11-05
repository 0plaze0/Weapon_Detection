FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

COPY --chown=user . .

# CPU-only torch keeps the image small
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir .

ADD --chown=user https://github.com/<user>/weapon-detection/releases/download/v1.0/best.pt weights/best.pt

EXPOSE 7860
CMD ["weapon-serve", "--host", "0.0.0.0", "--port", "7860"]`