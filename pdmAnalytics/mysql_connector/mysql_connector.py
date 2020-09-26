from mysql.connector import (connection)
import sys

MAX_ROW = sys.maxsize


class MySQLPdM:
    """
    Class definition for connecting the pdmAnalytics module to MySQL database.
      @config - database configuration
    """

    def __init__(self, config):
        self.cnx = connection.MySQLConnection(**config)

    def query_time_series(self, schema, table_name, column, start_row):
        """
        Query the MySQL Database.
          @self -The caller object,
          @table_name - table to select,
          @column - column to select in addition to timestamp,
          @start_row - Row number to start the query from
        """
        cursor = self.cnx.cursor()
        query = (
            f'SELECT {column}, timestamp FROM {schema}.{table_name} LIMIT {start_row}, {MAX_ROW}')
        cursor.execute(query)
        data = []
        for row in cursor:
            data.append(row)
        sequence = cursor.column_names
        next_start_row = start_row + cursor.rowcount
        cursor.close()
        return data, sequence, next_start_row

    def __del__(self):
        self.cnx.close
