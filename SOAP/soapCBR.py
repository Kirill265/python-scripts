from SOAPpy import SOAPProxy
from SOAPpy import Types
from SOAPpy.version import __version__

'''
namespace = "http://web.cbr.ru/"
url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
soapaction = "http://web.cbr.ru/EnumReutersValutesXML"
#input = Types.dateType(name = (namespace, "On_date"))

proxy = SOAPProxy(url, namespace = namespace, soapaction = soapaction)
proxy.config.debug = 1
proxy.EnumReutersValutesXML(input)

'''

namespace = "http://web.cbr.ru/"
url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
soapaction = "http://web.cbr.ru/GetCursOnDate"
input = Types.dateType(name = (namespace, "On_date"))

proxy = SOAPProxy(url, namespace = namespace, soapaction = soapaction)
proxy.config.debug = 1
proxy.GetCursOnDate(input)
