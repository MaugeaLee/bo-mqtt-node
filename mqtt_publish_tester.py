
# 본 스크립트는 mqtt device가 N개 존재한다는 가정으로 publish와 subscribe를 시뮬레이션 하기 위해 작성되었습니다.
# 본 스크립트는 반드시 debug용으로만 사용되어야 하며 모듈 개발 용으로 사용되어서는 안됩니다.
# 본 스크립트는 반드시 단독으로 사용됩니다.
# 본 스크립트는 network_mqtt.py 모듈과 network_reader.py 모듈에 의존하고 있습니다.
# 본 스크립트는 어떠한 의존성 파일도 수정해서는 안됩니다.
from network_mqtt import *
from concurrent.futures import ThreadPoolExecutor
import time

class MqttMultiTester(BoNetworkMQTT):
    def __init__(self, broker, port, id, pw, identity:str):
        super().__init__(broker, port, id, pw, identity)
        self.identity = identity # BO1A12 형식의 device_name
        self.client.on_message = self.on_message
    # override
    def on_message(self, client, userdata, message):
        self.network_conf['device_info']['device_name'] = self.identity
        self.network_conf['topic']['response_topic'] = f"response/{self.identity}/device-status"
        super().on_message(client, userdata, message)


def simulate_mqtt_device_task(identity):
    client = MqttMultiTester(broker=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, id=MQTT_USERNAME, pw=MQTT_PASSWORD,
                             identity=identity)
    client.connect()
    client.loop_forever()

if __name__ == '__main__':
    NUM_DEVICES = 99
    print(f'총 {NUM_DEVICES}개의 가상 MQTT 디바이스를 ON 합니다.')

    # 스레드 풀 생성
    with ThreadPoolExecutor(max_workers=NUM_DEVICES) as executor:
        for i in range(1, NUM_DEVICES + 1):
            identity = f"BO01B{i:02}"
            executor.submit(simulate_mqtt_device_task, identity)

    print("모든 디바이스가 백그라운드에서 작동 중입니다. Ctrl+C를 눌러 종료하세요")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("프로그램 종료 중 ...") # with 구문이 자동으로 종료 처리