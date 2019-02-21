FROM ubuntu:cosmic-20190131

MAINTAINER Jeremiah H. Savage <jeremiahsavage@gmail.com>

ENV version 0.4

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y \
       python3-pip \
    && apt-get clean \
    && pip3 install bam_readgroup_to_gdc_json \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache