cp -r /home/ec2-user/projects/aafsc/* /var/www/myproject/
chown -R nginx:nginx /var/www/myproject
find /var/www/myproject -type d -exec chmod 755 {} \;
find /var/www/myproject -type f -exec chmod 644 {} \;
