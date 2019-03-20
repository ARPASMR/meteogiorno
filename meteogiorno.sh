#!/bin/bash
#=============================================================================
# Lo script è all'interno di un container e produce i contenuti per il bollettino meteogiorno 
#
# ogni giorno:
# -esegue uno script python che interroga il DBmeteo e postgresIRIS e produce la mappa dei pluviometri,  
# -esegue uno script shell che interroga il DBmeteo e i file climatici e produce la tabella clima
# -carica gli output su Minio 
#
# 2018/11/22 MR
# 2019/03/20 MR GC UA aggiunta produzione tabella clima
#=============================================================================
numsec=86400   # 60 * 60 * 24 -> 1 gg

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
if [[ ($elapsed_time -eq 06) || ($SECONDS -ge $numsec) ]]
then 

################### produzione mappe pluvio

PLUVIO_GIORNO_PY='pluvio_giorno.py'
ieri=$(date --date="yesterday" +"%Y-%m-%d")
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
   FILE_TABELLA='Tabella_Clima.txt'
   ./Tclima_giorno.sh
 
 # verifico se è andato a buon fine
   STATO=$?
   echo "STATO USCITA DA script tabella clima ====> "$STATO

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
   SECONDS=0
   sleep $numsec
fi
done
exit 0
