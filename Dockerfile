FROM python:3.13-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Força o Python a enxergar os pacotes a partir da raiz /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tudo (incluindo a pasta src/) para dentro do container
COPY . .

EXPOSE 5000

# Executa o app.py que agora está dentro da pasta src no container
CMD ["python", "src/app.py"]
