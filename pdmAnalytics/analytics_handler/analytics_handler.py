from multiprocessing import Pool
import pandas as pd
from sklearn.linear_model import LinearRegression
import mysql_connector.mysql_connector as mysql


class AnalyticsHandler:

    def __init__(self, mysql_config, mysql_database, mqtt_config):
        self.mysql_config = mysql_config
        self.mysql_database = mysql_database
        self.mqtt_config = mqtt_config
        self.count_rows = [0] * mysql_database["linear_reg"]["num_lr"]
        self.first_pre_done = False
        self.first_predict = None

    def on_new_actuation(self, client, userdata, message):
        with Pool(5) as p:
            lr_list_of_dict = p.starmap(self.lr_predict, zip(
                self.mysql_database["linear_reg"]["table_names"],
                self.mysql_database["linear_reg"]["columns"], self.count_rows))
        p.join()
        # print(lr_list_of_dict)
        for row in lr_list_of_dict:
            for key, info in row.items():
                if (key != 'db_start_row'):
                    self.rl_reward_observe(key, info)
                else:
                    self.count_rows = [info] * \
                        self.mysql_database["linear_reg"]["num_lr"]

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to broker with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.mqtt_config["topics"]["event_trigger"])

    def lr_predict(self, table_name, column_name, start_row):
        mysql_connector = mysql.MySQLPdM(self.mysql_config)
        """
         Query the time series data of a given column and return
         the data, corresponding column names in sequence, and next
         starting row
        """
        data, sequence, next_start_row = mysql_connector.query_time_series(
            self.mysql_database["schema"], table_name, column_name, start_row)
        # convert mysql table to pandas DataFrame
        series = pd.DataFrame(data, columns=list(sequence))

        # Perform Linear Regression of the given dataset
        series['timestamp'] = pd.to_datetime(
            series['timestamp']).astype(int)
        # Convert time from ns to secs
        series['timestamp'] = series['timestamp']/1000000000
        Y = series.iloc[:, series.columns.get_loc(
            column_name)].values.reshape(-1, 1)
        X = series.iloc[:, series.columns.get_loc(
            'timestamp')].values.reshape(-1, 1)
        linear_regressor = LinearRegression()
        linear_regressor.fit(X, Y)
        linear_regressor.predict(X)

        # Forecast trend towards the future point in time
        last_index = len(series.index)-1
        pt_prediction_secs_interval = int(
            self.mysql_database["linear_reg"]["metadata"]["pt_prediction_secs_interval"])

        p = linear_regressor.coef_ * \
            ((X[last_index]-X[0] + pt_prediction_secs_interval)) + Y[0]
        diff = int(p - Y[last_index])

        # Place the forecasted information in a dictionary
        lr_dict = {table_name: {column_name: {"p": diff, "latest_val": int(Y[last_index])}},
                   'db_start_row': next_start_row}

        del mysql_connector
        return lr_dict

    def rl_reward_observe(self, key, dict_value):
        print(f'Linear Regression for {key} station: {dict_value}')
        forecasted_dictionary = {}
        global sub_key
        for sub_key, info in dict_value.items():
            print(f'Forecasted dictionary for {sub_key}:  {info}')
            forecasted_dictionary = info
        print(sub_key)
        print(f'forecasted_dictionary: {forecasted_dictionary}')
        forecasted_value = forecasted_dictionary['p'] + \
            forecasted_dictionary['latest_val']
        print(f'forecasted_value: {forecasted_value}')

    def send_rl_feedback(self):
        '''
        this function shoud publish RL observastion and rewards to MQTT
        '''
        ...
