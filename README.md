_Tested with python 3.8.5_

# Scribbly
Simple ToDo application written with Flask.

### Project setup
1. Change `.env.template` file name to `.env`
2. Setup `venv` and install dependencies
```
>> python -m pip install --upgrade pip
>> pip install -r requirements.txt
>> pip install -r requirements-dev.txt
```
3. Setup database
```
>> flask db upgrade
```
4. Run flask
```
>> flask run-eventlet
```

### pre-commit checks
To install pre-commit hooks in local repository (_MyPy has to be installed locally for pre-commit_):
```
>> pre-commit install
```
To run pre-commit hooks without commiting:
```
>> pre-commit run --all-files
```

### Migrations
To update database
```
>> flask db migrate -m <migration_slug>
>> flask db upgrade
```
