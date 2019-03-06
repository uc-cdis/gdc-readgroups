FROM ubuntu:cosmic-20190131

MAINTAINER Jeremiah H. Savage <jeremiahsavage@gmail.com>

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y \
       python3-pip \
       samtools \
    && apt-get clean \
    && pip3 install gdc_readgroups==0.1 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache
