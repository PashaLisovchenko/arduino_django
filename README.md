# RecSys Python/Django
Apache virtualhost file example for deploy
  ```bash
    Alias /static /var/www/arduino_django/boards/static
    <Directory /var/www/arduino_django/boards/static>
        Require all granted
    </Directory>
 <Directory /var/www/arduino_django/arduino_django/>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

	WSGIDaemonProcess sampleapp python-path=/var/www/arduino_django/:/home/uadmin/recsystem/lib/python3.6/site-packages
WSGIProcessGroup sampleapp
	WSGIScriptAlias / /var/www/arduino_django/arduino_django/wsgi.py
	ErrorLog ${APACHE_LOG_DIR}/recSys_error.log
	CustomLog ${APACHE_LOG_DIR}/recSys_access.log combined
</VirtualHost>
```
Построение рекомендательной системы по подбору плат для разработчиков.
