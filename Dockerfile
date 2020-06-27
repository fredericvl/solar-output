FROM python:alpine

WORKDIR /usr/src/app

ENV IP_ADDRESS=192.168.1.101
ENV PVOUTPUT_SYSTEM_ID=12345
ENV PVOUTPUT_API_KEY=my_secret_api_key

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY solar-output.py ./

CMD [ "python", "./solar-output.py" ]
