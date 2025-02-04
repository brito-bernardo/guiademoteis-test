# Usa uma imagem oficial do Python como base
FROM python:3.11

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas os arquivos necessários para instalar dependências (melhora cache)
COPY requirements.txt .

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto para o container
COPY . .

# Instala Node.js e npx (necessário para Prisma)
RUN apt update && apt install -y nodejs npm

# Garante que o Prisma Client Python está instalado
RUN pip install prisma

# Inicializa o Prisma Client dentro do container
RUN npx prisma generate

# Exibe os arquivos da pasta prisma (para debug)
RUN ls -l /app/prisma

# Comando padrão para iniciar a aplicação
CMD ["python", "main.py"]
