installing and running the autostart service:
documentation: https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd

enable autostart steps:

sudo cp mmhome.service /etc/systemd/system/
sudo systemctl daemon-reload # needed for the system to see the file
sudo systemctl enable mmhome.service # enables the auto-start service

disable autostart steps:

sudo systemctl disable mmhome.service

manually operating the service:

sudo systemctl start mmhome.service
sudo systemctl stop mmhome.service
sudo systemctl restart mmhome.service
sudo systemctl status mmhome.service
