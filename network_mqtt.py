from dataclasses import dataclass

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
    def __init__(self, broker="localhost", port=1883):
        self.__network_conf = self.__config_open()
        self.broker = broker
        self.port = port

        # 클라이언트 생성
        self.client = mqtt.Client(client_id=self.__network_conf["device_name"])

        # callback 선언
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def __config_open(self):
        """ network_conf.json 종속 파일을 open하는 함수"""
        with open("network_conf.json", "r", encoding="utf-8") as f:
            network_conf = json.load(f)
        return network_conf

    def __config_wirte(self, ):
        """ network_conf.json 종속 파일을 덮어 씌우는 함수"""
        with open("network_conf.json", "w", encoding="utf-8") as f:
            pass

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.__network_conf["request_topic"])
        print("Connected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        # request topic으로 전송이 왔을 시의 로직
        if msg.topic == self.__network_conf["request_topic"]:
            request_signal = bool(msg.payload.decode("utf-8"))
            if request_signal == True:
                # network 정보 스캔
                publish_ip, local_ip, mac, interface = self.__network_scanner()

                # json 파일 갱신
                self.__network_conf['publish_ip'] = publish_ip
                self.__network_conf['local_ip'] = local_ip
                self.__network_conf['mac'] = mac
                self.__network_conf['interface'] = interface
                self.__network_conf['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open('network_conf.json', 'w', encoding="utf-8") as f:
                    json.dump(self.__network_conf, f)

                client.publish(self.__network_conf['response_topic'], str(self.__network_conf), qos=1, retain=True)
                print("publishing " + str(self.__network_conf))

    @staticmethod
    def __network_scanner():
        network_summary = network_reader.get_network_summary()  # 네트워크 정보 조회
        publish_ip = network_reader.get_publish_ip()  # 공용 ip 조회
        local_ip = network_reader.get_local_ip()
        local_ip = network_reader.get_summary_used_search(local_ip, network_summary)  # 사용중인 인터페이스 조회
        return publish_ip, local_ip['ip'], local_ip['mac'], local_ip['interface']


    def connect(self):
        self.client.connect(self.broker, self.port)

    def disconnect(self):
        self.client.disconnect()

    def loop_forever(self):
        self.client.loop_forever()

if __name__ == "__main__":
    client = BoNetworkMQTT()
    client.connect()
    client.loop_forever()