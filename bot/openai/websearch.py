import requests
import json
import re
from common.log import logger


# 接口的URL（替换为你的实际服务器地址）
class websearch:
    def search(query):
        url = "http://43.134.191.31:10010/chat"

        # 要发送的消息内容
        payload = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }

        # 请求头，指定内容类型为 JSON
        headers = {
            "Content-Type": "application/json"
        }
        res = ""
        try:
            # 发送 POST 请求
            logger.info("[WebSearch] payload: {}".format(payload))
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            # 检查响应状态码
            logger.info("[WebSearch] response: {}".format(response))
            if response.status_code == 200:
                # 解析返回的 JSON 数据
                response_data = response.json()
                res = response_data['content']
                print("接口返回内容:", response_data)
            else:
                print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")

        except requests.exceptions.RequestException as e:
            print("请求出错:", e)
        return res

    def judgeSearchIntent(query):
        search_keywords = re.compile(
            r'(搜索|查找|查一下|查询|寻找|哪里可以|如何|怎么|怎样|天气|推荐|推荐一下|获取|资讯|信息|资料|了解|知道|问一下|了解一下|帮我找|找一下|检索|查阅|how to|find|search|weather|recommend|lookup|query|get|info|information|recommendation|look for|where to)',
            flags=re.IGNORECASE
        )
        logger.info("[WebSearch] Start intent judgement of: {}".format(query))
        return bool(search_keywords.search(query))
