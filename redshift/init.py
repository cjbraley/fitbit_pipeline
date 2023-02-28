from redshift import get_redshift_connection, get_raw_schema_query, get_intraday_create_table_query, get_sleep_create_table_query

intraday_resources = [
    {"name": "heart", "type": "INTEGER"},
    {"name": "steps", "type": "INTEGER"},
    {"name": "distance", "type": "FLOAT"},
]

if __name__ == "__main__":
    engine = get_redshift_connection()

    schema_query = get_raw_schema_query()
    sleep_table_query = get_sleep_create_table_query()

    # run queries
    with engine.connect() as con:
        con.execute(schema_query)
        con.execute(sleep_table_query)

        for resource in intraday_resources:
            table_query = get_intraday_create_table_query(
                resource['name'], resource['type'])
            con.execute(table_query)
