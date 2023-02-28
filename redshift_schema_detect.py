from redshift_auto_schema import RedshiftAutoSchema
import psycopg2 as pg
import dotenv
import os

dotenv.load_dotenv()  # use .env file

BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
REDSHIFT_CLUSTER_HOST = os.environ.get('REDSHIFT_CLUSTER_HOST')
REDSHIFT_CLUSTER_PORT = os.environ.get('REDSHIFT_CLUSTER_PORT')
REDSHIFT_SCHEMA_RAW = os.environ.get('REDSHIFT_SCHEMA_RAW')
REDSHIFT_ADMIN_USER = os.environ.get('TF_VAR_REDSHIFT_ADMIN_USER')
REDSHIFT_PW = os.environ.get('TF_VAR_REDSHIFT_PW')
REDSHIFT_DATABASE_NAME = os.environ.get('TF_VAR_REDSHIFT_DATABASE_NAME')

connection_string = f'postgresql://{REDSHIFT_ADMIN_USER}:{REDSHIFT_PW}@{REDSHIFT_CLUSTER_HOST}:{REDSHIFT_CLUSTER_PORT}/{REDSHIFT_DATABASE_NAME}'
print(connection_string)


redshift_conn = pg.connect(connection_string)

new_table = RedshiftAutoSchema(file='sleep.parquet',
                               schema='test_schema',
                               table='test_table',
                               conn=redshift_conn)


ddl = new_table.generate_table_ddl()
print(ddl)
