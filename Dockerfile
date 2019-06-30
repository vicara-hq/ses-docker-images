FROM ubuntu:18.04
ARG download_url
RUN apt-get -qq update > /dev/null && apt-get -qq install -y libx11-6 libfreetype6 libxrender1 libfontconfig1 libxext6 xvfb curl > /dev/null
RUN Xvfb :1 -screen 0 1024x768x16 &
RUN curl ${download_url} -o ses.tar.gz && \
tar -zxf ses.tar.gz
COPY run-segger-setup.sh .
RUN chmod +x run-segger-setup.sh && ./run-segger-setup.sh
