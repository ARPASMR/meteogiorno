#!/bin/bash
#--------------

# scriptino per generare il file di precompilazione per tabella clima meteogiorno

# aprile, 2018
# MS & UA

#marzo, 2019
# MR, UA & GC - lettura DB e dockerizzazione
#----------------------------------------------------------------------
# dichiarazioni

  DATAI=$(date --date="yesterday" +%Y-%m-%d)
  DATAF=$(date --date="today" +%Y-%m-%d)
  DD=$(date --date="yesterday" +%m-%d)
  DATACLIMA="2010-"$DD 

# intestazione file di output

echo "SITO" > Tabella_Clima.txt
echo "Tmin, Tmax" >> Tabella_Clima.txt
echo "Tmin_CLIMA, Tmax_CLIMA" >> Tabella_Clima.txt

#compilazione file di output

  for sito in Milano Brescia Sondrio Pavia Mantova 
  do

	echo "" >> Tabella_Clima.txt 
	echo "$sito" >> Tabella_Clima.txt 
	
	case $sito in
	     Milano)      
		 IDSENSORE=5897 ;;
	    Brescia)      
		 IDSENSORE=2414 ;;
	    Sondrio)
		 IDSENSORE=2096 ;;
	    Pavia) 
		 IDSENSORE=8157 ;;
     	Mantova)
		 IDSENSORE=5121 ;;
	esac

# recupero tmin e tmax dal DBmeteo
  MINMAX=`mysql -u guardone -pguardone -D METEO --execute 'select min(Misura) as Tmin, max(Misura) as Tmax from M_Termometri where IDsensore='$IDSENSORE' and Data_e_ora>="'$DATAI'" and Data_e_ora<"'$DATAF'";' --silent --raw`
echo "$MINMAX" >> Tabella_Clima.txt 

# recupero tmin e tmax del clima da apposito file
  VETTORE_MAX_CLIMA=($(grep $DATACLIMA Massima_81-10_$sito.txt))
  VETTORE_MIN_CLIMA=($(grep $DATACLIMA Minima_81-10_$sito.txt))
  echo "${VETTORE_MIN_CLIMA[1]} ${VETTORE_MAX_CLIMA[1]}" >> Tabella_Clima.txt 
  done
 




