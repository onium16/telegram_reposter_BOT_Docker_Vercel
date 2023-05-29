FROM python:3.11.2
WORKDIR /app
COPY requirements.txt requirements.txt
COPY docker-compose.yml docker-compose.yml
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 755 .
COPY . .
CMD [ "python", "./api/index.py" ]
 
 