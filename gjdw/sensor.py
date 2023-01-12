"""
Support for guojiadianwang
# Author:
    freefitter
# Created:
    2020/9/2
"""
import logging
import json
import time, datetime
from dateutil.relativedelta import relativedelta 
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, ATTR_ATTRIBUTION, CONF_ID
    )
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import requests
from bs4 import BeautifulSoup


_Log=logging.getLogger(__name__)

DEFAULT_NAME = 'gjdw'
OPENID = 'openid'
NONCESTR = 'noncestr'
SIGN = 'sign'
UNIONID = 'unionid'
TIMESTAMP1 = 'timestamp'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(OPENID): cv.string,
	vol.Required(NONCESTR): cv.string,
	vol.Required(SIGN): cv.string,
	vol.Required(UNIONID): cv.string,
	vol.Required(TIMESTAMP1): cv.string,
    vol.Optional(CONF_NAME, default= DEFAULT_NAME): cv.string,
})

HEADERS = {
    'Host': 'weixin.js.sgcc.com.cn',
    'Connection':  'keep-alive',
    'Content-Length': '0',
    'content-type': 'application/json',
    'Accept-Encoding': 'gzip,compress,br,deflate',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000026) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/wx203b37ad2ad5d2a6/32/page-frame.html',
}

API_URL = "https://weixin.js.sgcc.com.cn/wxapp_dlsh/wx/oauth_executeNewMini.do"
def setup_platform(hass, config, add_devices, discovery_info=None):
    sensor_name = config.get(CONF_NAME)
    openid = config.get(OPENID)
    noncestr = config.get(NONCESTR)
    sign = config.get(SIGN)
    unionid = config.get(UNIONID)
    timestamp1 = config.get(TIMESTAMP1)
    url = API_URL + "?openid=" + openid +"&timestamp=" + timestamp1 + "&noncestr=" + noncestr + "&sign=" + sign + "&unionid=" + unionid + "&userInfo=null"    
    _Log.info("url:" + url )
    add_devices([GJDW(sensor_name,url,openid,unionid)])

class GJDW(Entity):
    """Representation of a guojiadianwang """
    def __init__(self,sensor_name,url,openid,unionid):
        self.attributes = {}
        self._state = None
        self._name = sensor_name
        self._url = url
        self._openid = openid
        self._unionid = unionid

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """   mdi   ."""
        return 'mdi:flash'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attributes

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return "元"

    def update(self):
        try:
            """_Log.error("url:" + self._url)"""
            response = requests.post(self._url,headers = HEADERS)
        except ReadTimeout:
            _Log.error("Connection timeout....")
        except ConnectionError:
            _Log.error("Connection Error....")
        except RequestException:
            _Log.error("Unknown Error")
        res = response.content.decode('utf-8')
        if res.find("html") >= 0 :
            _Log.error("参数存在问题,请重新抓包填写")
            return
            """_Log.error(res)"""
        else:
        	_Log.info("请求成功.....")
        ret = json.loads(res)
        if ret["errcode"] == "0000":
            if "owe_amt" in ret["yeModel"] :
                self._state = ret["yeModel"]["owe_amt"]
                self.attributes['rca_flag'] = ret["yeModel"]["rca_flag"]
                self.attributes['cur_amt'] = ret["yeModel"]["cur_amt"]
                curfeeMsg = json.loads(ret["curfee"])
                self.attributes['ymd'] = curfeeMsg["ymd"]
                self.attributes['totalMoney'] = curfeeMsg["totalMoney"]
                self.attributes['powerSum'] = curfeeMsg["powerSum"]
                dbObjMsg = json.loads(ret["dbObj"])
                self.attributes['stepNo'] = dbObjMsg["stepNo"]
                self.attributes['yearAmount'] = dbObjMsg["yearAmount"]
            else:
            	self.attributes['rca_flag'] = '-1'
            	self.attributes['cur_amt'] = '-1'
            	_Log.error("yeModel is null !")
            # 更新url参数 
            url = API_URL + "?openid=" + self._openid +"&timestamp=" + ret["timestamp"] + "&noncestr=" + ret["noncestr"] + "&sign=" + ret["sign"] + "&unionid=" + self._unionid + "&userInfo=null" 
            self._url = url
        else:
            _Log.error("send request error....")
        

