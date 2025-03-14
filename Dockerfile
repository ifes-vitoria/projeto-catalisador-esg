FROM ubuntu:20.04

# Diretório de trabalho
WORKDIR /app

# Definir o fuso horário para evitar prompt de configuração
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    apt-get update && apt-get install -y tzdata && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Definir PYTHONPATH
ENV PYTHONPATH=/app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    libpq-dev \
    gcc \
    python3-dev \
    libssl-dev \
    libffi-dev \
    wkhtmltopdf

# Instalar dependências Python
RUN apt-get install -y python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install --no-cache-dir fastapi uvicorn jinja2 pydantic sqlalchemy python-multipart reportlab psycopg2 pandas matplotlib pdfkit

# Copiar código da aplicação
COPY . /app

# Comando para inicializar o banco de dados e rodar a aplicação
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["python", "db_manager.py", "&&", "uvicorn","main:app","--host","0.0.0.0","--port","8000","--reload" ]
