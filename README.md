# tmm-webinfo

Webinfo pro šifrovačky na Táboře mladých matematiků

## How to run

### Before first run

1. Rename `tmm_webinfo.example.yaml` to `tmm_webinfo.yaml` and fill in the details (for debugging using a local SQLite database, remove
   the `db` section).
2. Prepare the database:
    ```shell
    py create_db.py
    ```

### Run

```shell
py -m flask run 
```
