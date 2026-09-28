# Imagem base oficial do Python
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Instalação de dependências de sistema para SQLite e PDFs
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o CATS-SESP
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]