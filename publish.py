import paho.mqtt.client as mqtt
from network_reader import *
import time
import json


broker = "localhost"
port = 1883
topic = "test/topic"

print(f"{__name__}")
print("Connecting to broker...")
print(f"broker: {broker}  port: {port}  topic: {topic}")

client = mqtt.Client()
client.connect(broker, port)

print("connecting to broker...")

last_value = None
while True:
    network = get_network_summary()
    local_ip = get_local_ip()
    local_ip = get_summary_used_search(local_ip, network)

    # 값 변경 이벤트 감지하기
    if local_ip != last_value:
        print(f"publishing {local_ip} to {topic}")
        last_value = local_ip

        # conf 파일을 open 하여 종속 파일 참조하기
        with open("network_conf.json", "r", encoding="utf-8") as f:
            network_conf = json.load(f)
        network_conf

        # publish 발행
        client.publish(topic, str(last_value), qos=1)

    time.sleep(5)
