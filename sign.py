import logger
import json
import requests
import time
from login import get_cookies
import random
import hashlib
import os

# PC端签到接口
# sign_url = "https://tieba.baidu.com/sign/add"

# 移动端签到接口
sign_url = "https://c.tieba.baidu.com/c/c/forum/sign"

# 通知信息
notice = ""


# 单个贴吧签到
# tieba_name:贴吧名
def tieba_sign_in(tieba_name, tbs, BDUSS):
    global notice
    sign_str = f"kw={tieba_name}tbs={tbs}tiebaclient!!!"
    sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
    payload = {
        "kw": tieba_name,
        "tbs": tbs,
        "sign": sign,
    }
    Cookies = {
        "BDUSS": BDUSS,
    }
    resp = requests.post(
        sign_url,
        cookies=Cookies,
        data=payload,
    )
    
    try:
        json_resp = resp.json()
        if "user_info" in json_resp:
            logger.debug("签到成功：" + tieba_name + "吧")
            notice += "签到成功：" + tieba_name + "吧" + '\n'
            return True
        elif json_resp["error_code"] == "160002":
            # 已签到
            logger.error(
                "签到失败：" + tieba_name + "吧" + " 失败原因：" + json_resp["error_msg"]
            )
            notice += "签到失败：" + tieba_name + "吧" + "，失败原因：" + json_resp["error_msg"] + '\n'
        else:
            logger.error("签到失败：" + tieba_name + "吧")
            logger.debug(str(json_resp))
            logger.error("失败原因：" + json_resp["error_msg"])
            notice += "签到失败：" + tieba_name + "吧" + "，失败原因：" + json_resp["error_msg"] + '\n'
    except Exception as e:
        logger.error("签到失败：" + tieba_name + "吧")
        logger.error("报错：" + str(e))
        logger.debug("返回数据：" + resp.text)
        notice += "签到失败：" + tieba_name + "吧" + "，报错了!!!" + '\n'
        return False
    
    return False


def sign_in():
    global notice
    logger.info("开始签到\n")
    with open("tieba_dict.json", "r", encoding="utf-8") as f:
        tieba_dict = json.load(f)
    sign_sum, faliure_sum = 0, 0
    tbs, BDUSS, _ = get_cookies()
    for tieba_name, tieba_url in tieba_dict.items():
        if tieba_sign_in(tieba_name, tbs, BDUSS) == False:
            faliure_sum += 1
        sign_sum += 1
        logger.info("第" + str(sign_sum) + "个吧")
        logger.info("已签到成功" + str(sign_sum - faliure_sum) + "个吧\n")
        time.sleep(random.randint(1, 5))

    logger.info("共计" + str(sign_sum) + "个贴吧：成功" + str(sign_sum - faliure_sum) + "个，失败" + str(faliure_sum) + "个。")
    
    if 'SendKey' in os.environ:
        notice += "共计" + str(sign_sum) + "个贴吧：成功" + str(sign_sum - faliure_sum) + "个，失败" + str(faliure_sum) + "个。"
        api = f'https://sctapi.ftqq.com/{os.environ["SendKey"]}.send'
        title = "贴吧签到，共计" + str(sign_sum) + "个：成功" + str(sign_sum - faliure_sum) + "个，失败" + str(faliure_sum) + "个"
        data = {
        "title":title,
        "desp":notice
        }
        try:
            req = requests.post(api, data=data, timeout=60)
            if req.status_code == 200:
                logger.info("Server酱通知发送成功：" + title)
            else:
                logger.info(f"通知失败，状态码：{req.status_code}")
                logger.info(api)
        except Exception as e:
            logger.error(f"通知发送异常：{e}")


# if __name__ == "__main__":
#     tieba_name = "余额宝"
#     tieba_url = "https://tieba.baidu.com/f?kw=%D3%E0%B6%EE%B1%A6"
#     logger.set_logger("debug")
#     tieba_sign_in(tieba_name, tieba_url)
