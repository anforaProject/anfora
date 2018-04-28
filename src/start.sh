rm zinat.db
./clone.sh
python populate.py

gunicorn -b :$1 main:app \
	 --keep-alive 5 \
	 --reload \
	 --log-level DEBUG \
	 --workers 3
