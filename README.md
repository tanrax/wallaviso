# Install

```bash
pip install -r requirements.txt
cp envExample .env
```

Config *.env*
 
## Database

```bash
python3 models.py db init
python3 models.py db migrate
python3 models.py db upgrade
```
 
# Run
 
## Web
 
```bash
python3 app.py
```

## Tasks (send notifications)

```bash
python3 tasks.py notify
```

# Test
 
```bash
python3 test.py
```
