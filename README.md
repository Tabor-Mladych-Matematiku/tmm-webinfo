# tmm-webinfo

Webinfo pro šifrovačky na Táboře mladých matematiků

## How to run

### Before first run

1. Install the requirements:
   ```shell
   py -m pip install -r requirements.txt
   ```
2. Rename `tmm_webinfo.example.yaml` to `tmm_webinfo.yaml` and fill in the details (for debugging using a local SQLite database, remove
   the `db` section).

3. Prepare the database:
    ```shell
    py create_db.py
    ```

### Run (for development)

```shell
py -m flask --app tmm_webinfo run 
```

## Deployment

The [PythonAnywhere](https://eu.pythonanywhere.com/) free hosting can be used to deploy the app. They have a [A beginner's guide to building a simple database-backed Flask website on PythonAnywhere](https://blog.pythonanywhere.com/121/) which can serve as a reference for creating an account there and setting up the database. However, it is not a tutorial for deploying an existing project so instead of writing the code of the app according to the tutorial, this repository can be cloned (using a console) and the *WSGI configuration file* updated accordingly to set `project_home` and import `from tmm_webinfo import app as application`.
