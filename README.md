Steps to install invmgd on DUT
================================
- On Linux server
```
  1. apt-get install python3-stdeb (build-essential python3-all dh-python, etc...)
  2. git clone <this repository>
  3. cd invmgd; ./build_deb.sh
  4. copy output python3-invmgd_0.1-1_all.deb to DUT
```
- On DUT
```
  1. pip3 install required packages 
  2. dpkg -i python3-invmgd_0.1-1_all.deb
  3. edit /etc/invmgd/config.ini for correct sql server's hostname/port
  4. systemctl start invmgd.service
  5. troubleshooting with the /var/log/invmgd.log
```
