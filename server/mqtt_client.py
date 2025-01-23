import time
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"

POST_TOPIC = "request/get"
GET_TOPIC = "request/post"

class MqttClient:
    def __init__(self):
        self.client = mqtt.Client()
        print(f"Łączenie z brokerem MQTT: {BROKER_ADDRESS}")
        self.client.connect(BROKER_ADDRESS)
        print("Połączono z brokerem MQTT.")
        self.callbacks = {}
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()

    def publish(self, subtopic, msg_str):
        self.client.publish(POST_TOPIC, f"{subtopic};{msg_str}")
        
    def set_callback(self, subtopic, callback):
        self.callbacks[subtopic] = callback
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Połączono z brokerem MQTT. Subskrypcja tematu:", GET_TOPIC)
            client.subscribe(GET_TOPIC)
        else:
            print("Błąd połączenia. Kod=", rc)
            
    def on_message(self, client, userdata, msg):
        msg_str = msg.payload.decode("utf-8")
        subtopic, msg_str = msg_str.split(";")
        print(f"received: {msg_str}")
        if subtopic in self.callbacks:
            self.callbacks[subtopic](msg_str)
        else:
            print("Nieobsługiwany temat:", subtopic)
        