import json
import re
import requests
import urllib.parse
# 1. 对用户输入的地区名称进行 URL 编码
def name_change(name):
    encoded_name = urllib.parse.quote(name)
    return encoded_name
# 2. 获取地区的经纬度
def get_latitude_longitude(url):
    """获取 API 数据并解析纬度、经度"""
    response = requests.get(url)

    # **方法 1：去掉 JSONP 包装**
    json_text = re.sub(r"^ng_jsonp_callback_\d+\((.*)\);?$", r"\1", response.text)  # 提取括号内 JSON 数据

    try:
        data = json.loads(json_text)  # 解析 JSON
        results = data.get("results", [])

        if results:  # 确保 results 不为空
            lat = results[0]["geometry"]["lat"]
            lng = results[0]["geometry"]["lng"]
            return lat, lng
        else:
            print("❌ 没有找到位置信息")
            return None, None

    except json.JSONDecodeError:
        print("❌ JSON 解析失败")
        return None, None


# 3. 获取 GHI, GTI, OPTA 数据
def get_GHI_GTI_OPTA(url2):
    """获取光照数据"""
    response = requests.get(url2)
    try:
        data = response.json()
        GHI = data["annual"]["data"]['GHI']
        GTI = data["annual"]["data"]['GTI_opta']
        OPTA = data["annual"]["data"]['OPTA']
        return GHI, GTI, OPTA
    except KeyError as e:
        print(f"❌ 数据解析失败，缺少字段: {e}")
        return None, None, None
    except json.JSONDecodeError:
        print("❌ JSON 解析失败")
        return None, None, None


# 主函数
if __name__ == '__main__':
    name = input("请输入想获取的地区: ")
    area = name_change(name)  # 对输入的地区名称进行 URL 编码
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }

    # 获取地区经纬度
    url = f"https://api.opencagedata.com/geocode/v1/json?q={area}&key=08c837016a914d4a8b7db3f8d8ed1d90&no_annotations=1&language=zh&jsonp=ng_jsonp_callback_5"
    latitude, longitude = get_latitude_longitude(url)

    if latitude and longitude:
        # 获取光照数据
        url2 = f"https://apps.solargis.com/api/data/lta?loc={latitude},{longitude}"
        GHI, GTI, OPTA = get_GHI_GTI_OPTA(url2)

        # 输出结果
        print(f"地区的纬度: {latitude}, 经度: {longitude}")
        if GHI is not None and GTI is not None and OPTA is not None:
            print(f"GHI: {GHI}, GTI: {GTI}, OPTA: {OPTA}")
        else:
            print("❌ 光照数据获取失败")
    else:
        print("❌ 无法获取有效的纬度和经度")