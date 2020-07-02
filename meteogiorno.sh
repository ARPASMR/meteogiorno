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
#=============================================================================

export https_proxy="http://proxy2:8080"
export http_proxy="http://proxy2:8080"

#numsec=86400   # 60 * 60 * 24 -> 1 gg
numsec=10800  # 3 ore

S3CMD='s3cmd --config=config_minio.txt'

SECONDS=$numsec

putS3() {
  path=$1
  file=$2
  aws_path=$3
  bucket=$4
  date=$(date -R)
  acl="x-amz-acl:public-read"
  content_type='application/x-compressed-tar'
  string="PUT\n\n$content_type\n$date\n$acl\n/$bucket/$aws_path$file"
  signature=$(echo -en "${string}" | openssl sha1 -hmac "${S3SECRET}" -binary | base64)
  curl -X PUT -T "$path/$file" \
    --progress-bar \
    -H "Host: $S3HOST" \
    -H "Date: $date" \
    -H "Content-Type: $content_type" \
    -H "$acl" \
    -H "Authorization: AWS ${S3KEY}:$signature" \
    "http://$S3HOST/$bucket/$aws_path$file"
}

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
   else # caricamento su MINIO 
       putS3 . $FILE_PNG meteogiorno/ rete-monitoraggio 

       # controllo sul caricamento su MINIO 
       if [ $? -ne 0 ]
       then
         echo "problema caricamento su MINIO"
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
   else # caricamento su MINIO 
       putS3 . $FILE_TABELLA meteogiorno/ rete-monitoraggio 


       # controllo sul caricamento su MINIO 
       if [ $? -ne 0 ]
       then
         echo "problema caricamento su MINIO"
         exit 1
       fi
   fi

   rm -f $FILE_TABELLA


################### produzione immagine sinottica
#SINOTTICA_PY='sinottica.py'
#IMMAGINE_SINOTTICA='sinottica'$ieri'.png'
    
#    python $SINOTTICA_PY
 
# # verifico se è andato a buon fine
#   STATO=$?
#   echo "STATO USCITA DA "$ $SINOTTICA_PY" ====> "$STATO#

#   if [ "$STATO" -eq 1 ] # se si sono verificate anomalie esci 
#   then
#       exit 1
#   else # caricamento su MINIO 
#       putS3 . $IMMAGINE_SINOTTICA meteogiorno/ rete-monitoraggio 

#       # controllo sul caricamento su MINIO 
#       if [ $? -ne 0 ]
#       then
#         echo "problema caricamento su MINIO"
#         exit 1
#       fi
#   fi

#   rm -f $IMMAGINE_SINOTTICA
   
   
   
  ################# pulizia cartella di minio
  periodo="5 days"
  $S3CMD --config=config_minio.txt ls s3://rete-monitoraggio/meteogiorno/ | while read -r line;
  do
    createDate=`echo $line|awk {'print $1'}`
    createDate=`date -d"$createDate" +%s`
    olderThan=`date -d"-$periodo" +%s`
    if [[ $createDate -lt $olderThan ]]
      then
        fileName=`echo $line|awk {'print $4'}`
        if [[ $fileName != "" ]]
          then
          $S3CMD del "$fileName"
        fi
    fi
  done;
  
  SECONDS=0
  sleep $numsec
fi
done
exit 0
