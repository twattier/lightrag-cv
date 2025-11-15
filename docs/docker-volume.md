use https://github.com/offen/docker-volume-backup


# Trigger a backup manually

You can manually trigger a backup run outside of the defined cron schedule by executing the backup command inside the container:

docker exec <container_ref> backup
==> docker exec lightrag-cv-backup backup


If the container is configured to run multiple schedules, you can source the respective conf file before invoking the command:

docker exec <container_ref> /bin/sh -c 'set -a; source /etc/dockervolumebackup/conf.d/myconf.env; set +a && backup'

# Restore volumes from a backup

In case you need to restore a volume from a backup, the most straight forward procedure to do so would be:

Stop the container(s) that are using the volume
Untar the backup you want to restore

tar -C /tmp -xvf  backup.tar.gz

Using a temporary once-off container, mount the volume (the example assumes it’s named data) and copy over the backup. Make sure you copy the correct path level (this depends on how you mount your volume into the backup container), you might need to strip some leading elements

docker run -d --name temp_restore_container -v data:/backup_restore alpine
docker cp /tmp/backup/data-backup temp_restore_container:/backup_restore
docker stop temp_restore_container
docker rm temp_restore_container

Restart the container(s) that are using the volume
Depending on your setup and the application(s) you are running, this might involve other steps to be taken still.

If you want to rollback an entire volume to an earlier backup snapshot (recommended for database volumes):

Trigger a manual backup if necessary (see Manually triggering a backup).
Stop the container(s) that are using the volume.
If volume was initially created using docker-compose, find out exact volume name using:
docker volume ls

Remove existing volume (the example assumes it’s named data):
docker volume rm data

Create new volume with the same name and restore a snapshot:
docker run --rm -it -v data:/backup/my-app-backup -v /path/to/local_backups:/archive:ro alpine tar -xvzf /archive/full_backup_filename.tar.gz

==>
docker run --rm -it -v lightrag-cv-postgres-data:/backup/postgres_data -v ./data/backups:/archive:ro alpine tar -xvzf /archive/backup-2025-11-15T01-05-28.tar.gz

Restart the container(s) that are using the volume.