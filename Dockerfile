FROM ubuntu:cosmic-20190131

MAINTAINER Jeremiah H. Savage <jeremiahsavage@gmail.com>

ENV version 0.9

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y \
       python3-pip \
       samtools \
    && apt-get clean \
    && pip3 install bam_readgroup_to_gdc_json==0.9 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache