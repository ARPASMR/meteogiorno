FROM arpasmr/python_base:conda
COPY . /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts
RUN apt-get install -y s3cmd
RUN apt-get install -y vim
CMD ["./meteogiorno.sh"]
