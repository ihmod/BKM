1.使用，导入项目

2.加载依赖

如果下载慢，可以尝试修改源

教程： https://blog.csdn.net/xqnode/article/details/88431139

3.确保你要抢购的商品已经在购物车

4.本地有谷歌浏览器和谷歌浏览器驱动，驱动可以放在python根目录下

5.调整时间参数

内置了get_localtime()和get_time()两个

在最后提交订单的那一步可选

get_localtime():获取本地时间，也就是以本地时间为准

get_time()：通过请求获取的淘宝的时间戳，校准时间45ms，也可以尝试不校准试试



总之，关键就是保证点击的时机和淘宝时间一致
