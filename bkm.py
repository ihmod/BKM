import datetime
import json
import logging
import re
import time
from logging import handlers
from time import sleep

import pyttsx3
import requests
from selenium.webdriver.support import expected_conditions as EC
import colorlog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# 模块初始化
engine = pyttsx3.init()

# 语音播报内容
content = " 人生苦短，我用 pai sin"

# 淘宝官网
tb ='https://www.taobao.com/'

# 结算的时间差，4s的时候点结算 单位毫秒
jiesuan=-7000
# 提交订单的时间差,在允许时间的50毫秒内点击提交
tijiao=10
# 获取淘宝时间的配置
url1 = 'http://acs.m.taobao.com/gw/mtop.common.getTimestamp/'
url2 = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43'
}


# 模拟器选项
Options = webdriver.ChromeOptions()
# 引入不关闭浏览器的相关配置项
Options.add_experimental_option("detach", True)
# 避免终端下执行代码报警告
Options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
# 以下两行代码解决支付宝支付页面对webdriver的检测
# Options = webdriver.ChromeOptions()
# Options.add_argument("disable-blink-features=AutomationControlled")


# 日志配置
colors_config = {
    # 终端输出日志颜色配置
    'DEBUG': 'white',
    'INFO': 'cyan',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

default_formats = {
    # 终端输出格式
    'color_format': '%(log_color)s%(asctime)s.%(msecs)03d---%(levelname)s  %(message)s',
    # 日志输出格式
    'log_format': '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
}
formatter1 = colorlog.ColoredFormatter(default_formats["color_format"], log_colors=colors_config,datefmt='%Y-%m-%d %H:%M:%S')
formatter2 = logging.Formatter(default_formats["log_format"])
# banner配置
yellow = '\033[01;33m'
white = '\033[01;37m'
green = '\033[01;32m'
blue = '\033[01;34m'
red = '\033[1;31m'
end = '\033[0m'
banner = f'''项目启动
{yellow}
宝可梦计划 #V0.0.1
-------------------------------------------------------------------------
{green}
 ██████                      ██   ██         ████     ████                         
░█░░░░██                    ░██  ██         ░██░██   ██░██                   █████ 
░█   ░██   ██████    ██████ ░██ ██    █████ ░██░░██ ██ ░██  █████  ███████  ██░░░██
░██████   ░░░░░░██  ██░░░░██░████    ██░░░██░██ ░░███  ░██ ██░░░██░░██░░░██░██  ░██
░█░░░░ ██  ███████ ░██   ░██░██░██  ░███████░██  ░░█   ░██░███████ ░██  ░██░░██████
░█    ░██ ██░░░░██ ░██   ░██░██░░██ ░██░░░░ ░██   ░    ░██░██░░░░  ░██  ░██ ░░░░░██
░███████ ░░████████░░██████ ░██ ░░██░░██████░██        ░██░░██████ ███  ░██  █████ 
░░░░░░░   ░░░░░░░░  ░░░░░░  ░░   ░░  ░░░░░░ ░░         ░░  ░░░░░░ ░░░   ░░  ░░░░░  

'''
# 获取淘宝时间戳 13位 毫秒级
def get_time():
    get_data = requests.get(url1, headers=headers)
    data = json.loads(get_data.text)
    return int(data['data']['t'])+45

# 使用本地时间
def get_localtime():
    t=time.time()
    return int(t*1000)
# 日志定义
def logdefine():
    logger = logging.getLogger()  # 创建记录器
    logger.setLevel(level=logging.DEBUG)  # 设置记录级别

    # 输出到控制台
    stream_handler = logging.StreamHandler()  # 输出流位置
    stream_handler.setLevel(logging.INFO)  # 输出级别
    stream_handler.setFormatter(formatter1)  # 输出格式

    # 保存日志文件，并自动分割器，按文件大小分割
    rotating_file_handler = handlers.RotatingFileHandler(filename='./日志.log', mode='a', maxBytes=10 * 1024 * 1024,
                                                         backupCount=2, encoding='utf-8')
    rotating_file_handler.setLevel(logging.INFO)
    rotating_file_handler.setFormatter(formatter2)

    logger.addHandler(rotating_file_handler)  # 添加分割器的日志输出
    logger.addHandler(stream_handler)  # 设置输出流到控制台
    return logger


# 判断是否为空
def isNotEmpty(variable):
    if isinstance(variable, str) and variable == "":
        return False
    else:
        return True

# 判断传入值合法性
def detect(time):
    # 判断传入值都不为空
    f1 = isNotEmpty(time)
    # 同时为True继续进行,否则返回False：数据为空
    if f1 :
        # 正则匹配字符串
        t = re.match(r'([0-1]\d|2[0-3]):[0-5]\d', time)
        # u = re.match(r'https://.*', url, re.I)
        # 返回的对象是否为真，同时为真代表符合规则，否则返回false：数据格式不对
        if bool(t) :
            return True
        else:
            return False
    else:
        logger.error("数据为空")
        return False

# 时间格式化
def timeFormat(a):
    stime = datetime.date.today().strftime(f'''%Y-%m-%d {a}:%S.%f''')
    return stime

# 二维码登录
def loginByScan(browser):
    logger.info("正在尝试扫码登录")
    try:
        # 点击淘宝页面上方的”亲，请登录“
        browser.find_element(By.XPATH, '//*[@id="J_SiteNavLogin"]/div[1]/div[1]/a[1]').click()
        # 在登录页面点击二维码进行扫码登陆
        browser.find_element(By.XPATH, '//*[@id="login"]/div[1]/i').click()
        # 设置显示等待条件，等页面加载出购物车dom停止等待
        flag = EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.member-cart'))
        logger.info("请在两分钟内完成扫码登录")
        element = WebDriverWait(browser, 120).until(flag)
    except:
        browser.close()
        logger.error("操作超时")
    else:
        # 根据获取元素判断是否成功登录
        if element:
            logger.info("扫码登录成功")
            try:
                my_cookie = browser.get_cookies()
                with open('./cookies.txt', 'w') as file:
                    file.write(str(my_cookie))
            except:
                logger.warning("cookies写入失败")
            else:
                logger.info("cookies写入成功")

        else:
            browser.close()
            logger.error("操作失败")

    return browser

# cookies自动登录
def loginByCookies(browser):
    try:
        # 将获取到的cookie进行注入
        with open('./cookies.txt', 'r') as file:
            # 读取cookie并转换为python的字典
            result = eval(file.read())
        for i in result:
            # 将每一个cookie字典注入到网页中
            # cookie中可能会涉及到一个secure安全性字段，一般情况下此字段不会产生影响
            if i['secure'] == True:
                browser.add_cookie(i)
        browser.refresh()
    except:
        logger.warning("cookies登录失败")
        return None
    else:
        logger.info("登录成功")
        return browser


#   登录
def login():
    # 打开浏览器
    browser = webdriver.Chrome(options=Options)
    # 访问淘宝
    browser.get(url=tb)
    b = loginByCookies(browser)
    if b==None:
        #扫码登录
        b = loginByScan(browser)
    return b

# 下单
def order(browser,stime):
    browser.get("https://cart.taobao.com/cart.htm")

    # 先转换为时间数组
    timeArray = time.strptime(stime, "%Y-%m-%d %H:%M:%S.%f")

    # 转换为时间戳
    buyStamp = int(time.mktime(timeArray))*1000
    logger.info("进入等待刷新时间，现在请复制要抢购的商品复选框ID")
    # 等待刷新
    while True:
        #时间间隔大于120秒的时候，刷新一下沉睡20秒
        if buyStamp-get_time() > 120000:
            browser.get("https://cart.taobao.com/cart.htm")
            sleep(20)
            logger.info("还有{}秒".format(int((buyStamp-get_time())/1000)))
        else:
            logger.info("最后两分钟，准备抢购")
            break
    # logger.info("ID格式   J_CheckBox_5268705480405,J_CheckBox_5268705480405  多个ID 用’,‘隔开 ")
    # logger.warning("请输入商品复选框ID（不设置则默认全选）")
    # list=input().split(",")
    #   选中商品
    while True:
        try:
            # if len(list)!=0:
            #     logger.info("1")
            #     for i in range(0,len(list)) :
            #         logger.info(list[i])
            #         browser.find_element(By.ID, list[i]).click()
            #     logger.info("已经选中需要的商品")
            #     break
            # else:
            #     logger.info("2")
            if browser.find_element(By.ID, "J_SelectAll1"):
                browser.find_element(By.ID, "J_SelectAll1").click()
                logger.info("已经选中全部商品")
                break
        except:
            logger.error("未选中商品")
            break
#     点击结算
    while True:
        if get_localtime() - buyStamp >= jiesuan:
            try:
                browser.find_element(By.LINK_TEXT, "结 算").click()
                logger.info("结算点击成功")
                break
            except:
                logger.error("😥没点到结算")
                break
        else:
            logger.info("还有{}秒".format(float((buyStamp-get_time())/1000)))

#     点击提交订单
    while True:
        t = get_time()
        if t - buyStamp >= tijiao:
            try:
                browser.find_element(By.LINK_TEXT, '提交订单').click()
                logger.info("提交时间{}".format(t))
                # 设置要播报的Unicode字符串
                engine.say(content)

                # 等待语音播报完毕
                engine.runAndWait()
                break
            except:
                logger.error("😅还是太慢了")
                break


# 主函数
def main():

        logger.info("时间格式 00:00 ")
        logger.warning("请输入抢购时间:")
        time = input()

        logger.info(banner)
        # 检测数据合理性
        if detect(time):
            stime = timeFormat(time)
            logger.info("抢购时间 "+stime[:-3])
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            if stime > now:
                # 登录
                driver=login()
                # 登录成功就下单
                order(driver,stime)
            else:
                logger.error("时间早于当前时间，不可抢购")
        else:
            logger.error("数据格式不对")

# 原神
if __name__ == "__main__":
    # 创建日志
    logger = logdefine()
    main()