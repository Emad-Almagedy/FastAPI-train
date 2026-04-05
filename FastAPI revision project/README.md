# USING ALEMBIC FOR DATABASE MIGRATION

1. when making edits to the database the new columns will be ignored and you will have to delete the entire database and recreate it to see the changes. with Alembic `it will run a script to ALTER the existing table, adding a new column without deleting any of the data`

2. it will be used for version control, where we can rollback to a previous version.

3. users autogenerateto compare the current SQlAlchemy models to the actual databases and write migration script automatically 

4. Alembic will build the same structure on the new, bigger database automatically when you scale from SQlite to PostgreSQL or MySQL

5. you will have to delete the database first to start with it.

6. check if PostgreSQL is installed `psql --version`

7. to set a user and database on windows

"# Windows (installer):
psql -U postgres -c "CREATE USER bloguser WITH PASSWORD 'blogpass';"
createdb -U postgres -O bloguser blog"

or 
`first login as master user psql -U postgres`
`CREATE USER webuser WITH PASSWORD 'webpass';`
`CREATE DATABASE donations OWNER webuser;`

8. to verify check `psql donations -U webuser`

9. files to be updated (add the  database_url to config settings and .env, update the lifespan function in the main.py)

10. run `uv run alembic init -t async alembic` then we will need to update the alembic.ini and env.py in the alembic folder and remove the databaseURL and link the one in the .env in the database folder.

11. we will generate our first migration using alembic `uv run alembic revision --autogenerate -m "initial schema"` this will create a file. and then apply the migration ` uv run alembic upgrade head`( heck by using psql blog -U bloguser and then \dt and \d TABLENAME for specific tables)

12. to check the current state `uv run alembic current`

13. using the uv `run alembic revision... `command to make a new change if we add somthing to the models and then run `uv run alembic upgrade head` to stage it to the postgre database. run `uv run alembic current` to check where you are and `uv run alembic history` to check the history

# note: 
1. add compare type setting as true in alembic env.py (to detect column type type changes in the alembic)
2. we will run the alembic upgrade head once in production of all the commits.


