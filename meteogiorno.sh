#!/bin/bash
#=============================================================================
# Lo script è all'interno di un container e produce i contenuti per il bollettino meteogiorno
#
# ogni tre ore produce le seguenti mappe relative al giorno precedente:
# -esegue uno script python che interroga il DBmeteo e postgresIRIS e produce la mappa dei pluviometri,
# -esegue uno script python che interroga il DBmeteo e i file climatici e produce la tabella clima
# (-esegue uno script pyton che recupera i wms e genera la immagine sinottica)
# -carica gli output su Minio
# - cancella da Minio i file più vecchi di 5 giorni
#
# 2018/11/22 MR
# 2019/03/20 MR GC UA aggiunta produzione tabella clima
# 2019/04/09 aggiunta produzione immagine sinottica
# 2020/07/02 rimossa produzione immagine sinottica
# 2021/10/14 sostituita copia su nasprevisore a copia su minio
#=============================================================================

export https_proxy="http://proxy2:8080"
export http_proxy="http://proxy2:8080"

export IRIS_USER_ID=postgres
export IRIS_USER_PWD=p0stgr3S
export IRIS_DB_NAME=iris_base
export IRIS_DB_HOST=10.10.0.19
export MYSQL_USER_ID=guardone
export MYSQL_USER_PWD=guardone
export MYSQL_DB_NAME=METEO
export MYSQL_DB_HOST=10.10.0.25
export MYSQL_DB_PORT=3308

nas_usr='ARPA\svcMeteo%woT$ln5=lProp1&w'
NAS=//10.10.0.44/F
putdir=PRECOMPILAZIONE/MeteoGIORNO
fake=arpav-gagliard

#numsec=86400   # 60 * 60 * 24 -> 1 gg
numsec=10800  # 3 ore

S3CMD='s3cmd --config=config_minio.txt'

SECONDS=$numsec

#
elapsed_time=$(date +%H)
while [ 1 ]
do
# procedi sono se è passato numsec dall'ultimo invio
if [[ ($elapsed_time -eq 07) || ($SECONDS -ge $numsec) ]]
then


 ieri=$(date --date="yesterday" +"%Y-%m-%d")
################### produzione mappe pluvio

 PLUVIO_GIORNO_PY='pluvio_giorno.py'
 FILE_PNG='pluvio_giorno_'$ieri'.png'

    python $PLUVIO_GIORNO_PY

   # verifico se è andato a buon fine
   STATO=$?
   echo "STATO USCITA DA "$ $PLUVIO_GIORNO_PY" ====> "$STATO

   if [ "$STATO" -eq 1 ] # se si sono verificate anomalie esci
   then
       exit 1
   else # caricamento su nasprevisore
       smbclient -U $nas_usr $NAS -n $fake -c "prompt; cd ${putdir}; mput $FILE_PNG; quit"

       # controllo sul caricamento su nasprevisore
       if [ $? -ne 0 ]
       then
         echo "problema caricamento su nasPrevisore"
         exit 1
       fi
   fi
   rm -f $FILE_PNG

################### produzione tabella clima
 CLIMA_GIORNO_PY='Tclima_giorno.py'
 FILE_TABELLA='Tabella_Clima_'$ieri'.json'

      python $CLIMA_GIORNO_PY

 # verifico se è andato a buon fine
   STATO=$?
   echo "STATO USCITA DA "$ $CLIMA_GIORNO_PY" ====> "$STATO

   if [ "$STATO" -eq 1 ] # se si sono verificate anomalie esci
   then
       exit 1
   else # caricamento su nasprevisore
       smbclient -U $nas_usr $NAS -n $fake -c "prompt; cd ${putdir}; mput $FILE_TABELLA; quit"

       # controllo sul caricamento su nasprevisore
       if [ $? -ne 0 ]
       then
         echo "problema caricamento su NASprevisore"
         exit 1
       fi
   fi

   rm -f $FILE_TABELLA




  ################# pulizia cartella nasprevisore

dataref=$[$(date +%j) - 1]

# cancello file creati precedentemente a dataref

    list=$(smbclient -U $nas_usr $NAS -n $fake -c "prompt; cd $putdir; ls {pluvio_*.png,Tabella_*.json}; quit" | \
         awk '{ext="png"; ext2="json"; if (substr($1,length($1)-length(ext)+1,length(ext))==ext || substr($1,length($1)-length(ext2)+1,length(ext2))==ext2) print $1}')

     for i in $list
     do
             echo $i >>  /opt/sat/bin/lista_elim_pluvio_e_clima.txt
             detail=$(smbclient -U $nas_usr $NAS -n $fake -c "prompt; cd $putdir; allinfo $i; quit" | \
               grep "create_time:" | awk 'BEGIN{FS=" "}{print $2,$3,$4,$7}')
             datafile=$(date -d "$detail" +%j)
             if [ $datafile -lt $dataref ]
             then
                     echo "$(date +%d"/"%m"/"%Y"/"%H":"%M) -> $i" >>  /opt/sat/bin/lista_elim_pluvio_e_clima.txt
                     smbclient -U $nas_usr $NAS -n $fake -c "prompt; cd $putdir; del $i; quit"
            fi
     done


  SECONDS=0
  sleep $numsec
fi
done
exit 0
