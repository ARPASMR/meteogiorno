FROM arpasmr/python_base:conda
COPY . /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts
#CMD ["./meteogiorno.sh"]
