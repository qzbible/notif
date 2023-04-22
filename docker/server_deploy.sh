#! /bin/bash

if [ -z "$CONTABO_IP_ADDRESS" ]
then
    echo "CONTABO_IP_ADDRESS not defined"
    exit 0
fi

git archive --format tar --output ./projectNotif.tar develop

echo "Uploading the projectNotif.....:-)...Be Patient!"
rsync ./projectNotif.tar root@$CONTABO_IP_ADDRESS:/tmp/projectNotif.tar
echo "Upload complete....:-)"


echo "Building the image......."
ssh -o StrictHostKeyChecking=no root@$CONTABO_IP_ADDRESS << 'ENDSSH'
    mkdir -p /klivar_notif
    rm -rf /klivar_notif/* && tar -xf /tmp/projectNotif.tar -C /klivar_notif
    docker-compose -f /klivar_notif/production.yml build

ENDSSH
echo "Build completed successfully.......:-)"