#rm zinat.db
#./clone.sh
#python populate.py

gunicorn --bind 0.0.0.0:3000 main:app \
	 --keep-alive 5 \
	 --reload \
	 --log-level DEBUG \
	 --workers 3

#uwsgi uwsgi.ini
