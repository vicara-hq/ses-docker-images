ARG SES_DL=https://www.segger.com/downloads/embedded-studio/Setup_EmbeddedStudio_ARM_v560a_linux_x64.tar.gz
FROM ubuntu:20.04
ARG SES_DL

RUN apt-get update
RUN apt-get install -y wget python3 python3-pip libx11-6 libfreetype6 libxrender1 libfontconfig1 libxext6

RUN wget $SES_DL -O ses.tar.gz
RUN tar -zvxf ses.tar.gz
RUN echo "yes" | $(find arm_segger_* -name "install_segger*") --copy-files-to /ses
RUN rm ses.tar.gz
RUN rm -rf segger