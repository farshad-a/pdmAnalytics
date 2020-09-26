import mysql_connector.mysql_connector as mysql
import paho.mqtt.client as mqtt
import analytics_handler.analytics_handler as analytics
import json

if __name__ == "__main__":

    with open('config.json') as f:
        config = json.load(f)

    mysql_config = config["mysql"]["config"]
    mysql_database = config["mysql"]["database"]
    mqtt_config = config["mqtt"]

    client = mqtt.Client()
    handler = analytics.AnalyticsHandler(
        mysql_config, mysql_database, mqtt_config)

    client.on_message = handler.on_new_actuation
    client.on_connect = handler.on_connect
    client.connect("127.0.0.1", 1883, 60)

    client.loop_forever()
