# TakeMyMoney
![Shut up and take my money!](http://vignette2.wikia.nocookie.net/walkingdead/images/3/3f/Shut-up-and-take-my-money.jpg/revision/latest/scale-to-width-down/1280?cb=20140829235648)

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

## Tips
### Running .sql files without copy-and-pasting

Instead of copying the SQL statements into the `psql` terminal and running it there, you can also run the following command:
`psql -U postgres -d djangostack -a -f [.sql filename]`

This is especially useful for the database seed files, such as `funding.sql`, `users.sql` or `projects.sql`.

For this command to work, you have to be on the same folder as the `.sql` file.

**NOTE:** This command has a small issue where it doesn't update the `pid` / `user_id` sequences, so it breaks the registration/project creation flow. See the fix [below](#when-registering-a-new-user-or-adding-new-projects-the-database-attempts-to-add-a-piduser_id-starting-from-1-even-after-inserting-the-seed-data).

## Issues
### "The env.py file cannot be imported"

1. Copy `env.example.py`, paste it in the same folder with the name `env.py`.
2. Change the PASSWORD string in `env.py` to match your Djangostack installation details.

### "Relation does not exist"

This means that your database tables do not exist yet. To fix this, follow the steps:

1. Run the `use_djangostack` terminal.
2. Run `psql -U postgres djangostack`, and type in your password.
3. Copy the relevant content from `schema.sql` (in this repository) and paste in the terminal, press Enter.

### When registering a new user or adding new projects, the database attempts to add a `pid/user_id` starting from 1 even after inserting the seed data

This happens if we run the seed SQL queries from the bash terminal instead of copy-pasting the queries manually and running them from the psql terminal.

The `SERIAL` data type is implemented with a backing Postgres sequence - for our database these sequences are called `projects_pid_seq` and `users_user_id_seq`.

Whenever we `INSERT` into the `projects` table, the `pid` is automatically set with the next value on the sequence (you can see the next value in the sequence using `SELECT nextval('projects_pid_seq')`), and the sequence is also automatically advanced.

When we run the seed SQL queries from the bash terminal, for some reason the backing sequence is _not_ automatically advanced. This results in the next value on the sequence still staying at `1` even when we already have IDs up to `20` (for the `users` table) or `100` (for the projects table).

The fix is to manually set the sequence value to the correct number again, and this is done via the `setval` call, as such:

```sql
SELECT setval('projects_pid_seq', (SELECT MAX(pid) FROM projects));
SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users));
```
