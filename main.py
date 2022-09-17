import json
from urllib import parse, request
import ssl

deye_login_url = "https://api.deye.com.cn/v3/enduser/login/"
deye_device_list_url = "https://api.deye.com.cn/v3/enduser/deviceList/"
mqtt_info_url = "https://api.deye.com.cn/v3/enduser/mqttInfo/"

if __name__ == '__main__':
    print("请输入德业用户名密码")
    loginname = input("用户名：")
    password = input("密码：")
    while len(loginname) == 0 or len(password) == 0:
        print("用户名密码不能为空，请重新输入")
        loginname = input("用户名：")
        password = input("密码：")
    data = {"loginname": loginname,
            "password": password,
            "pushtype": "Ali",
            "extend": "{\"cid\":\"6a1db1eb00b14656870e3fe7d7123456\",\"type\":\"1\"}",
            "appid": "a774310e-a430-11e7-9d4c-00163e0c1b22"}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    encoded_data = parse.urlencode(data).encode()
    login_req = request.Request(deye_login_url, data=encoded_data)
    login_resp = request.urlopen(login_req, context=ctx)
    login_resp_json = json.loads(login_resp.read().decode("utf-8"))

    if login_resp_json["meta"]["code"] != 0:
        print("登录失败：" + str(login_resp_json))
        quit()

    token = login_resp_json["data"]["token"]
    clientid = login_resp_json["data"]["clientid"]

    mqtt_info_req = request.Request(mqtt_info_url)
    mqtt_info_req.add_header("Authorization", "JWT " + token)
    mqtt_info_resp = request.urlopen(mqtt_info_req, context=ctx)
    mqtt_info_resp_json = json.loads(mqtt_info_resp.read().decode("utf-8"))
    if mqtt_info_resp_json["meta"]["code"] != 0:
        print("mqtt信息获取失败：" + str(mqtt_info_resp_json))
        quit()

    mqtt_endpoint = mqtt_info_resp_json["data"]["endpoint"]
    print("")
    print("------------------------------")
    print("MQTT INFO:")
    print("mqtthost(broker): " + mqtt_info_resp_json["data"]["mqtthost"])
    print("mqttport: " + str(mqtt_info_resp_json["data"]["mqttport"]))
    print("sslport: " + str(mqtt_info_resp_json["data"]["sslport"]))
    print("username: " + mqtt_info_resp_json["data"]["loginname"])
    print("password: " + mqtt_info_resp_json["data"]["password"])
    print("clientid: " + mqtt_info_resp_json["data"]["clientid"])
    print("endpoint: " + mqtt_endpoint)
    print("")

    device_req = request.Request(deye_device_list_url)
    device_req.add_header("Authorization", "JWT " + token)
    device_resp = request.urlopen(device_req, context=ctx)
    device_resp_json = json.loads(device_resp.read().decode("utf-8"))
    if device_resp_json["meta"]["code"] != 0:
        print("获取设备列表失败：" + str(device_resp_json))
        quit()
    device_list = device_resp_json["data"]
    print("------------------------------")
    print("设备信息列表:")
    for device in device_list:
        product_id = device["product_id"]
        device_id = device["device_id"]
        print("--------------")
        print("设备名：" + device["device_name"])
        print("设备id：" + device_id)
        print("产品型号：" + device["product_name"])
        print("产品id：" + product_id)
        print("是否在线：" + str(device["online"]))
        print("MAC地址：" + device["mac"])

        # state_topic mqtt_endpoint/productid/deviceid/status/hex
        # command_topic mqtt_endpoint/productid/deviceid/command/hex
        print("state_topic: " + mqtt_endpoint + "/" + product_id + "/" + device_id + "/status/hex")
        print("command_topic: " + mqtt_endpoint + "/" + product_id + "/" + device_id + "/command/hex")
