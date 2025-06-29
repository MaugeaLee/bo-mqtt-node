import paho.mqtt.client as mqtt
from network_reader import *
import time
import json
import datetime


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
    publish_ip = get_publish_ip()
    network = get_network_summary()
    local_ip = get_local_ip()
    local_ip = get_summary_used_search(local_ip, network)

    # 값 변경 이벤트 감지하기
    if local_ip != last_value:
        last_value = local_ip

        # conf 파일을 open 하여 종속 파일 참조하기
        with open("network_conf.json", "r", encoding="utf-8") as f:
            network_conf = json.load(f)

        network_conf['publish_ip'] = publish_ip
        network_conf['local_ip'] = last_value['ip']
        network_conf['mac'] = last_value['mac']
        network_conf['interface'] = last_value['interface']
        network_conf['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 수정 파일 write 하기
        with open('network_conf.json', 'w', encoding="utf-8") as f:
            json.dump(network_conf, f)

        # publish 발행
        client.publish(topic, str(network_conf), qos=1, retain=True)
        print(f"publishing {str(network_conf)} to {topic}") # 로그

    time.sleep(5)
