from dataclasses import dataclass
import os
import yaml
from dotenv import load_dotenv

import paho.mqtt.client as mqtt
import network_reader
import json
import datetime

@dataclass
class BoNetworkInterface:
    domain: str
    device_name: str
    publish_ip: str
    local_ip: str
    mac: str
    interface: str
    time_stamp: str
    request_topic: str
    response_topic: str


class BoNetworkMQTT:
    def __init__(self, broker:str="localhost", port:int=1883, id:str="", pw:str="", identity:str|None=None):
        self.network_conf = self.__config_open_yaml()
        self.broker = broker
        self.port = port
        self.id = id
        self.pw = pw
        self.identity = identity

        # 클라이언트 생성
        if not identity:
            self.client = mqtt.Client(client_id=self.network_conf["device_info"]["device_name"])
        else:
            self.client = mqtt.Client(client_id=identity)

        # callback 선언
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def __config_open_yaml(self):
        try:
            with open("network_const.yaml", "r", encoding="utf-8") as f:
                try:
                    network_conf = yaml.safe_load(f)
                    return network_conf
                except yaml.YAMLError as error:
                    raise yaml.YAMLError(error) # yaml(상수) 파일이 open 되지 않으면 프로세스를 실행시킬 수 없습니다.
        except FileNotFoundError as e:
            raise FileNotFoundError(e)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.network_conf["topic"]["request_topic"])
        print("Connected with result code " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        client.unsubscribe(self.network_conf["topic"]["request_topic"])
        if rc == 0:
            print("Disconnected successfully")
        elif rc == 7:
            print("MQTT에 예상치 못한 Disconnected error 발생 with code " + str(rc))

    def on_message(self, client, userdata, msg):
        # request topic으로 전송이 왔을 시의 로직
        if msg.topic == self.network_conf["topic"]["request_topic"]:
            request_signal = bool(msg.payload.decode("utf-8"))
            if request_signal == True:
                # network 정보 스캔
                publish_ip, local_ip, mac, interface = self.__network_scanner()

                # json 파일 갱신
                self.network_conf["device_info"]["publish_ip"] = publish_ip
                self.network_conf["device_info"]["local_ip"] = local_ip
                self.network_conf["device_info"]["mac"] = mac
                self.network_conf["device_info"]["interface"] = interface
                self.network_conf["time_stamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # json 형태로 맞추기 위해 dumps 하고 publish 하기
                response_data_json = json.dumps(self.network_conf, indent=4, sort_keys=True)
                client.publish(self.network_conf["topic"]["response_topic"], response_data_json, qos=1, retain=False)

                print(f"publishing {self.network_conf['device_info']['domain']} "
                      f"{self.network_conf['device_info']['device_name']} - {self.network_conf['device_info']['local_ip']} - "
                      f"{self.network_conf['device_info']['mac']}")

    @staticmethod
    def __network_scanner():
        network_summary = network_reader.get_network_summary()  # 네트워크 정보 조회
        publish_ip = network_reader.get_publish_ip()  # 공용 ip 조회
        local_ip = network_reader.get_local_ip()
        local_ip = network_reader.get_summary_used_search(local_ip, network_summary)  # 사용중인 인터페이스 조회
        return publish_ip, local_ip["ip"], local_ip["mac"], local_ip["interface"]

    def connect(self):
        self.client.username_pw_set(username=self.id, password=self.pw)
        self.client.connect(self.broker, self.port)

    def disconnect(self):
        self.client.disconnect()

    def loop_forever(self):
        self.client.loop_forever()

load_dotenv(dotenv_path='mqtt_secret.env')

# 환경 변수 값 읽기
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = os.getenv("MQTT_BROKER_PORT")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

missing_vars = []
if not isinstance(MQTT_BROKER_HOST, str):
    missing_vars.append(MQTT_BROKER_HOST)
if not isinstance(MQTT_BROKER_PORT, str):
    missing_vars.append(MQTT_BROKER_PORT)
if not isinstance(MQTT_USERNAME, str):
    missing_vars.append(MQTT_USERNAME)
if not isinstance(MQTT_PASSWORD, str):
    missing_vars.append(MQTT_PASSWORD)\

if missing_vars:
    error_message = f"❌ 서버 초기화 실패: 다음 필수 환경 변수가 누락되었습니다: {', '.join(missing_vars)}"
    print(error_message)
    raise ValueError(error_message)

try:
    MQTT_BROKER_PORT = int(MQTT_BROKER_PORT)
except (ValueError, TypeError):
    error_message = f'❌ 서버 초기화 실패: MQTT_BROKER_PORT가 유효한 숫자가 아닙니다: {MQTT_BROKER_PORT}'
    print(error_message)
    raise ValueError(error_message)


if __name__ == "__main__":
    client = BoNetworkMQTT(broker=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, id=MQTT_USERNAME, pw=MQTT_PASSWORD)
    client.connect()
    client.loop_forever()