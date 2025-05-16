#!/bin/bash

# Fix permissions on Galera config
chmod 644 /etc/mysql/conf.d/galera.cnf

# Wait for MySQL to be ready
while ! mysqladmin ping -h"localhost" --silent; do
    sleep 1
done

# Create HAProxy check user and grant permissions
mysql -uroot -p${MYSQL_ROOT_PASSWORD} << EOF
CREATE USER IF NOT EXISTS 'haproxy_check'@'%' IDENTIFIED BY '';
GRANT USAGE ON *.* TO 'haproxy_check'@'%';

CREATE DATABASE IF NOT EXISTS event_booking;
USE event_booking;

CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON event_booking.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
EOF 