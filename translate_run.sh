#!/usr/bin/bash
while true;
do
time python3.9 -u translate_db.py | tee --append logs/log.txt
sleep 2000
done
