# Install

```bash
pipenv install
cp envExample .env
```

Config *.env*
 
## Database

```bash
pipenv shell
python3 models.py db init
python3 models.py db migrate
python3 models.py db upgrade
python3 models.py init_data
```
 
# Run
 
```bash
pipenv shell
python3 app.py
```
