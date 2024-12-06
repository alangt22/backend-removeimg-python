FROM python:3.10

# Configuração do diretório de trabalho
WORKDIR /app

# Copia os arquivos para o contêiner
COPY . /app

# Instala as dependências
RUN pip install -r requirements.txt

# Expõe a porta
EXPOSE 5000

# Inicia a aplicação com Gunicorn
CMD ["gunicorn", "remove:app", "--bind", "0.0.0.0:5000"]
