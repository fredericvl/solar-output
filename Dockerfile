FROM python:alpine

ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="fredericvl" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/fredericvl/solar-output" \
  org.opencontainers.image.source="https://github.com/fredericvl/solar-output" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="fredericvl" \
  org.opencontainers.image.title="saj-monitor" \
  org.opencontainers.image.description="Upload SAJ solar inverter data to PvOutput every 5 minutes" \
  org.opencontainers.image.licenses="MIT"

WORKDIR /usr/src/app

ENV IP_ADDRESS=192.168.1.101
ENV PVOUTPUT_SYSTEM_ID=12345
ENV PVOUTPUT_API_KEY=my_secret_api_key

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY solar-output.py ./

CMD [ "python", "./solar-output.py" ]
