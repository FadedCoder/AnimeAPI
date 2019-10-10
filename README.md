# AnimeAPI

Using:

1. Python (3.7+)
2. Django (2.2)
3. Celery (4.X)


## Installation Instructions

1. Install Python 3.7 (with venv and pip) including  on your machine. Installation instructions vary per OS. Google it up for your OS.
2. Install Redis and PostgreSQL. Installation instructions vary per OS. Google it up for your OS. `sudo systemctl enable --now redis postgres` if necessary.
3. Create a user and DB on PostgreSQL and enable extensions `pg_trgm` and `hstore`. Instructions for PSQL (on Linux):
```
sudo -u postgres -i
createuser -P --interactive
<Then enter a username and a password>
createdb -U <username> <db name>
```
After this is done, open [AnimeAPI/settings.py](https://github.com/FadedCoder/AnimeAPI/blob/master/AnimeAPI/settings.py#L79) and edit the DATABASE field. Enter your username, password and DB name.
4. On the base folder of this project, install venv and all the requirements. Steps for Linux (and Bash):
```
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```
5. (Optional) To make this into a production server, set `DEBUG=False` in [AnimeAPI/settings.py](https://github.com/FadedCoder/AnimeAPI/blob/master/AnimeAPI/settings.py#L26) and set it up as a reverse proxy with nginx or apache. Also run `python manage.py collectstatic` and serve static files with nginx or apache.
6. To run this, you can either set up a systemd file or use `screen`. Example:
```
screen
<press Enter>
source venv/bin/activate
python manage.py runserver 0.0.0.0:<insert port number>
```
