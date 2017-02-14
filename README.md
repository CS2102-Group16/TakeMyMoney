# TakeMyMoney
Shut up and take my money!

## Running instructions
1. Run `manager-osx` (for Mac) or `manager-windows` (for Windows)
 * Go to Manage Servers
 * Ensure that only the PostgreSQL Database is running
2. Run `use_djangostack`
 * For Windows, run `use_djangostack.bat`
 * For Mac, open Spotlight and run `use_djangostack`
3. While in the `use_djangostack` terminal:
 * Go to the directory containing the `manage.py` file.
 * Run `python manage.py runserver`. Your server should now be running at `localhost:8000`.

## Issues
### "The env.py file cannot be imported"

1. Copy `env.example.py`, paste it in the same folder with the name `env.py`.
2. Change the PASSWORD string in `env.py` to match your Djangostack installation details.

### "Relation does not exist"

This means that your database tables do not exist yet. To fix this, follow the steps:
1. Run the `use_djangostack` terminal.
2. Run `psql -U postgres djangostack`, and type in your password.
3. Copy the relevant content from `schema.sql` (in this repository) and paste in the terminal, press Enter.
