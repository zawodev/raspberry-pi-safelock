from admin_app import App
from mqtt_client import MqttClient
import database

if __name__ == "__main__":
    import os
    path = os.path.join(os.getcwd(), "database.db")
    #path = "mini-project/server/database.db"
    app = App(path)

    mqtt_client = MqttClient()

    def on_rfid_request(msg_str):
        print("Otrzymano żądanie RFID:", msg_str)
        app_response = app.add_request_mqtt("RFID", msg_str)
        mqtt_client.publish("RFID", app_response)
        print("Odpowiedź:", app_response)

    def on_encoder_request(msg_str):
        print("Otrzymano żądanie ENCODER:", msg_str)
        app_response = app.add_request_mqtt("ENCODER", msg_str)
        mqtt_client.publish("ENCODER_LOCK", app_response)
        print("Odpowiedź:", app_response)

        

    mqtt_client.set_callback("RFID", on_rfid_request)
    mqtt_client.set_callback("ENCODER_LOCK", on_encoder_request)

    #on_rfid_request("CARD_005,78392173647832,16.01.2025T10:01:01")
    #on_encoder_request("CARD_010:339,135,40,60,120,180,290,10")
    #on_encoder_request("CARD_010:340,135,40,60,120,180,290,10")

    app.mainloop()
