FROM python:3.11.2
WORKDIR /api
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 755 .
COPY . .
CMD [ "python", "./api/index.py" ]
 
 