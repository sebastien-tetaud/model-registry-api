# Dockerfile
FROM python:3.12-slim-bullseye

WORKDIR /usr/src/app
# Install git and any other dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN git clone https://github.com/tetaud-sebastien/model-registry.git

RUN pip install -e /usr/src/app/model-registry/.

# Set the default command to run the app (modify as per your app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "82", "--reload"]


