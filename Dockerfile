FROM arpasmr/python_base:conda
COPY . /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts
ARG secret
ENV https_proxy=https://${secret}@proxy2.arpa.local:8080/
ENV http_proxy=http://${secret}@proxy2.arpa.local:8080/
RUN apt-get update
RUN apt-get install -y smbclient
RUN apt-get install -y vim
CMD ["./meteogiorno.sh"]
