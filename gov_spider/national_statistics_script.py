# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: national_stastics.py
@ time: $18-11-14 下午2:34
"""
import requests
import time
import json
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_reg_code():
    """
    get reg code from html
    :return:
    """
    reg_html = """
    <ul> <li
    node = "{&quot;code&quot;:&quot;&quot;,&quot;name&quot;:&quot;序列&quot;,&quot;sort&quot;:&quot;4&quot;}"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 序列 </li> <li
    node = "{&quot;code&quot;:&quot;110000&quot;,&quot;name&quot;:&quot;北京市&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "110000"
    title = "北京市"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 北京市 </li> <li
    node = "{&quot;code&quot;:&quot;120000&quot;,&quot;name&quot;:&quot;天津市&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "120000"
    title = "天津市"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 天津市 </li> <li
    node = "{&quot;code&quot;:&quot;130000&quot;,&quot;name&quot;:&quot;河北省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "130000"
    title = "河北省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 河北省 </li> <li
    node = "{&quot;code&quot;:&quot;140000&quot;,&quot;name&quot;:&quot;山西省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "140000"
    title = "山西省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 山西省 </li> <li
    node = "{&quot;code&quot;:&quot;150000&quot;,&quot;name&quot;:&quot;内蒙古自治区&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "150000"
    title = "内蒙古自治区"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 内蒙古自治区 </li> <li
    node = "{&quot;code&quot;:&quot;210000&quot;,&quot;name&quot;:&quot;辽宁省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "210000"
    title = "辽宁省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 辽宁省 </li> <li
    node = "{&quot;code&quot;:&quot;220000&quot;,&quot;name&quot;:&quot;吉林省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "220000"
    title = "吉林省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 吉林省 </li> <li
    node = "{&quot;code&quot;:&quot;230000&quot;,&quot;name&quot;:&quot;黑龙江省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "230000"
    title = "黑龙江省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 黑龙江省 </li> <li
    node = "{&quot;code&quot;:&quot;310000&quot;,&quot;name&quot;:&quot;上海市&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "310000"
    title = "上海市"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 上海市 </li> <li
    node = "{&quot;code&quot;:&quot;320000&quot;,&quot;name&quot;:&quot;江苏省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "320000"
    title = "江苏省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 江苏省 </li> <li
    node = "{&quot;code&quot;:&quot;330000&quot;,&quot;name&quot;:&quot;浙江省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "330000"
    title = "浙江省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 浙江省 </li> <li
    node = "{&quot;code&quot;:&quot;340000&quot;,&quot;name&quot;:&quot;安徽省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "340000"
    title = "安徽省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 安徽省 </li> <li
    node = "{&quot;code&quot;:&quot;350000&quot;,&quot;name&quot;:&quot;福建省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "350000"
    title = "福建省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 福建省 </li> <li
    node = "{&quot;code&quot;:&quot;360000&quot;,&quot;name&quot;:&quot;江西省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "360000"
    title = "江西省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 江西省 </li> <li
    node = "{&quot;code&quot;:&quot;370000&quot;,&quot;name&quot;:&quot;山东省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "370000"
    title = "山东省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 山东省 </li> <li
    node = "{&quot;code&quot;:&quot;410000&quot;,&quot;name&quot;:&quot;河南省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "410000"
    title = "河南省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 河南省 </li> <li
    node = "{&quot;code&quot;:&quot;420000&quot;,&quot;name&quot;:&quot;湖北省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "420000"
    title = "湖北省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 湖北省 </li> <li
    node = "{&quot;code&quot;:&quot;430000&quot;,&quot;name&quot;:&quot;湖南省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "430000"
    title = "湖南省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 湖南省 </li> <li
    node = "{&quot;code&quot;:&quot;440000&quot;,&quot;name&quot;:&quot;广东省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "440000"
    title = "广东省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 广东省 </li> <li
    node = "{&quot;code&quot;:&quot;450000&quot;,&quot;name&quot;:&quot;广西壮族自治区&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "450000"
    title = "广西壮族自治区"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 广西壮族自治区 </li> <li
    node = "{&quot;code&quot;:&quot;460000&quot;,&quot;name&quot;:&quot;海南省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "460000"
    title = "海南省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 海南省 </li> <li
    node = "{&quot;code&quot;:&quot;500000&quot;,&quot;name&quot;:&quot;重庆市&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "500000"
    title = "重庆市"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 重庆市 </li> <li
    node = "{&quot;code&quot;:&quot;510000&quot;,&quot;name&quot;:&quot;四川省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "510000"
    title = "四川省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 四川省 </li> <li
    node = "{&quot;code&quot;:&quot;520000&quot;,&quot;name&quot;:&quot;贵州省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "520000"
    title = "贵州省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 贵州省 </li> <li
    node = "{&quot;code&quot;:&quot;530000&quot;,&quot;name&quot;:&quot;云南省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "530000"
    title = "云南省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 云南省 </li> <li
    node = "{&quot;code&quot;:&quot;540000&quot;,&quot;name&quot;:&quot;西藏自治区&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "540000"
    title = "西藏自治区"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 西藏自治区 </li> <li
    node = "{&quot;code&quot;:&quot;610000&quot;,&quot;name&quot;:&quot;陕西省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "610000"
    title = "陕西省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 陕西省 </li> <li
    node = "{&quot;code&quot;:&quot;620000&quot;,&quot;name&quot;:&quot;甘肃省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "620000"
    title = "甘肃省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 甘肃省 </li> <li
    node = "{&quot;code&quot;:&quot;630000&quot;,&quot;name&quot;:&quot;青海省&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "630000"
    title = "青海省"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 青海省 </li> <li
    node = "{&quot;code&quot;:&quot;640000&quot;,&quot;name&quot;:&quot;宁夏回族自治区&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "640000"
    title = "宁夏回族自治区"
    style = "border-bottom: 1px solid rgb(170, 170, 170);"> 宁夏回族自治区 </li> <li
    node = "{&quot;code&quot;:&quot;650000&quot;,&quot;name&quot;:&quot;新疆维吾尔自治区&quot;,&quot;sort&quot;:&quot;1&quot;}"
    code = "650000"
    title = "新疆维吾尔自治区"
    style = "border-bottom: none;"> 新疆维吾尔自治区 </li> </ul>
    """
    soup = BeautifulSoup(reg_html, 'html5lib')
    reg_list = list()
    tag_list= soup.find_all('li')
    for tag in tag_list[1:]:
        tag_info = tag.attrs.get('node')
        tag_info = json.loads(tag_info)
        reg_list.append({
            'name': tag_info.get('name'),
            'code': tag_info.get('code')
        })
    with open('reg_info.json', 'wb') as f:
        f.write(json.dumps(reg_list, ensure_ascii=False, indent=4))

def crawler_for_data():
    """
    爬取树型菜单中项目的数据
    :return:
    """
    data = {
        'm': 'QueryData',
        'dbcode': 'fsnd',
        'rowcode': 'zb',
        'colcode': 'sj',
        'wds': '[{"wdcode":"reg","valuecode":"110000"}]',
        'dfwds':'[{"wdcode":"zb","valuecode":"A0801"},{"wdcode":"sj","valuecode":"LAST20"}]',
        'k1': time.time()
    }
    headers = {
                # 'Accept': 'application/json, text/javascript, */*; q = 0.01',
                # 'Accept-Encoding':'gzip, deflate',
                # 'Accept-Language':'zh - CN, zh;q=0.8',
                # 'Connection':'keep - alive',
                # 'Cookie':'JSESSIONID = EAA6236B50B82D0BE7EEEAF435A8E99E;_trs_uv = j99acujt_6_hhro;experience = show;u = 6',
                # 'Host':'data.stats.gov.cn',
                # 'Referer':'http://data.stats.gov.cn/easyquery.htm?cn = E0103',
                # 'User-Agent': 'Mozilla/5.0(X11;Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko) Chrome / 60.0.3112.78 Safari / 537.36',
                # 'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.get('http://data.stats.gov.cn/easyquery.htm', params=data, headers=headers)
    result = json.loads(response.content)
    print result


def crawler_for_tree():
    """
    爬取统计局树型结构数据
    :return:
    """
    key_info = list()
    data = {
        'id': 'zb',
        'dbcode': 'fsnd',
        'wdcode': 'zb',
        'm': 'getTree'
    }
    response_1 = requests.post('http://data.stats.gov.cn/easyquery.htm', data=data)
    tree_info_1 = json.loads(response_1.content)
    for tree_1 in tree_info_1:
        key_1_info = {
            'id': tree_1.get('id'),
            'name': tree_1.get('name')
        }
        data = {
            'id': key_1_info['id'],
            'dbcode': 'fsnd',
            'wdcode': 'zb',
            'm': 'getTree'
        }
        response_2 = requests.post('http://data.stats.gov.cn/easyquery.htm', data=data)
        tree_info_2 = json.loads(response_2.content)
        for tree_2 in tree_info_2:
            key_2_info = {
                'id': tree_2.get('id'),
                'name': tree_2.get('name'),
                'parent_id': key_1_info['id'],
                'parent_name': key_1_info['name']
            }
            key_info.append(key_2_info)
    with open('key_code_info.json', 'wb') as f:
        f.write(json.dumps(key_info, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    # crawler_for_data()
    crawler_for_tree()

