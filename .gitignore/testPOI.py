
import urllib.request
import json
import math

apikey='254bfd619e12538e278002388d0e2564'
polygon_range='114.048818088108,22.548716905382|114.048855523004,22.528410644532|114.06902859158,22.528449164497|114.068712565105,22.548912760417|114.048818088108,22.548716905382'
keywords=''
POI_types='050300'                #change here to get diffrent types of poi

offset='20'
displayed_page='1'
extension='base'
outputfile=POI_types+'.txt'

#for coordinate system transformation
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

#get full url to request api
def url_amap_polygon(apikey,polygon_range,keywords,POI_types,offset,displayed_page,extension):
    fullurl='http://restapi.amap.com/v3/place/polygon?key='+apikey+'&polygon='+polygon_range+'&keywords='+keywords+'&types='+POI_types+'&offset='+offset+'&page='+displayed_page+'&extensions='+extension
    return fullurl

#send a request, and get result
def request_result(url):
    response = urllib.request.urlopen(url, timeout=1)
    html = response.read()
    decode_html = html.decode('utf-8')
    result = json.loads(decode_html)
    status=result['status']
    if status=='0':
        print('failed to get poi')

    return result
#check number of pages
def get_pagenumber(result,offset):
    pageset=int(offset)
    count =result['count']
    count_number=int(count)
    if (count_number%pageset)==0:
        pagenumber=int(count_number/pageset)
    else:
        pagenumber = int(count_number /pageset) + 1
    return pagenumber

#get longitude and latitude from a string
def getlongitude(location):

    List_longitude=[]
    List_location=list(location)

    for charecter in List_location:

        if (charecter==','):
            locationnumber=List_location.index(charecter)

            List_longitude=List_location[:locationnumber]

            break
    longitude=''.join(List_longitude)
    float_longitude=float(longitude)
    return float_longitude

def getlatitude(location):

    List_latitude=[]
    List_location=list(location)
    for charecter in List_location:
        if (charecter==','):
            locationnumber=List_location.index(charecter)
            List_latitude=List_location[locationnumber+1:]

            break
    latitude=''.join(List_latitude)
    float_latitude=float(latitude)
    return float_latitude

#transform coordinate system
def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """

    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
        0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
        0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


#first request, a test request to get page number
url=url_amap_polygon(apikey,polygon_range,keywords,POI_types,offset,displayed_page,extension)
result=request_result(url)
pagenumber=get_pagenumber(result,offset)
print(pagenumber)

#formal start, and record
with open(outputfile,'w',encoding='utf-8') as text_file:

    for i in range(pagenumber):
        row_count=0
        page=i+1
        str_page=str(page)
        url=url_amap_polygon(apikey,polygon_range,keywords,POI_types,offset,str_page,extension)
        result=[]
        result=request_result(url)

        for item in result['pois']:
            jname=item['name']
            jtypecode=item['typecode']
            jaddress=item['address']
            jlocation=item['location']
            jlon=getlongitude(jlocation)
            jlat=getlatitude(jlocation)
            wgs84location=gcj02towgs84(jlon,jlat)
            wgs84lon=wgs84location[0]
            wgs84lat=wgs84location[1]

            print(jname,'!',jtypecode,'!',jaddress,'!',wgs84lon,'!',wgs84lat,file=text_file)



