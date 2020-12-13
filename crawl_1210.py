import urllib.request
import requests
import urllib3
from bs4 import BeautifulSoup
import json
import re
import csv
import pandas as pd
import os

urllib3.disable_warnings()

f = open('output.csv', 'w', encoding='utf-8-sig', newline='')

wr = csv.writer(f)

wr.writerow(['시설명', '대표자', '연락처', '주소', '지도자', '시설면적', '운동종류', '장애종류', '강의명', '시간', '요일', '강사명', '기간', '차량지원', '장애 지원시설', '수강료'])

for i in range(145):
    url = "https://dvoucher.kspo.or.kr/course/memberFacilityList.do?menuNo=800002&topMenuNo=800001"

    header = {
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding" : "gzip, deflate, br",
    "Accept-Language" : "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control" : "max-age=0",
    "Connection" : "keep-alive",
    "Content-Length" : "241",
    "Content-Type" : "application/x-www-form-urlencoded",
    "Cookie" : "WT_FPC=id=240d3d64699174cab071606975323461:lv=1606975323461:ss=1606975323461; _INSIGHT_CK_1109=ca9e7e12b1af4127ae356fdac25cfaf3_75323|45f25b06c78562667f3b6fdac25cfaf3_75323:1606977723000; WMONID=GZthBgC1NTu; JSESSIONID=xozOOShKUBWsV9f2JuJZgGB7vmY9ckNvsvbi6449iDYmVcoOVsMlVSYE0S2pvoDW.amV1c19kb21haW4vZGFpc3kyX2R2ZnJvbnQx",
    "Host" : "dvoucher.kspo.or.kr",
    "Origin" : "https://dvoucher.kspo.or.kr",
    "Referer" : "https://dvoucher.kspo.or.kr/course/memberFacilityList.do?menuNo=800002&topMenuNo=800001",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    } 

    payload = {
        "pageNo" : i + 1
    }

    response = requests.post(url, data=payload, headers=header, verify=False)

    soup = BeautifulSoup(response.text, 'lxml')

    exercise = soup.find_all('button', class_ = 'btn-lec-view btn-type-6')

    fac_list = soup.find('ul', class_ = 'fac-info-list')

    # 시설명(한 페이지에 존재하는 개수만큼 리스트에 담김)
    name = [n.text for n in fac_list.find_all('a', href=True)]

    number = re.compile('[0-9]{10}')

    # 시설명에 해당하는 식별자(각 시설에서 운영하는 강좌를 긁어올 때 필요)
    result = number.findall(str(exercise))

    count = 0

    for j in result:
        url = "https://dvoucher.kspo.or.kr/course/memberFacilityCourseList.do"

        payload = {
            "bizrno" : j,
            "alsfcSn" : 1,
            "listUrl" : "/course/memberFacilityListJsonView.do",
            "detailUrl" : "/course/memberFacilityCourseList.do"
        }

        res = requests.post(url, data=payload, headers=header, verify=False)

        soup = BeautifulSoup(res.text, 'lxml')

        # 수강료
        try:
            fee = soup.find('div', class_ = 'class-ct-right').find('strong').text
        except AttributeError:
            fee = 0

        # 장애 지원 시설
        support = [i.text for i in soup.find('tbody').find_all('span')]
        support = [i for i in support if i]

        # 페이지 상단에 존재하는 시설 상세정보(대표자, 연락처, 주소, 지도자, 시설면적)
        info = [ii.text for ii in soup.find('div', class_ = 'fac-det-info').find_all('dd')]

        course = soup.find_all("dl", class_ = "class-ct-left")

        # 강좌들
        for i in course:
            tag1 = i.find("em", class_ = "purple").text # 보라색 태그
            tag2 = i.find("em", class_ = "green").text # 초록색 태그
            title = i.find("span").text # 강좌명
            time = i.find_all("p", class_ = "ff-light")[0].text # 시간
            day = i.find_all("p", class_ = "ff-light")[1].text # 요일
            teacher = i.find_all("p", class_ = "ff-light")[2].text.split() # 강사
            enroll = i.find_all("p", class_ = "ff-light")[3].text # 신청기간

            wr.writerow([name[count], info[0][6:], info[1][6:], info[2][5:],\
                info[3][23:], info[4][7:], tag1, tag2, title, time, day, ','.join(teacher), enroll, support[0], ','.join(support[1:]), fee])
                
        count += 1

        if count == len(name):
            count = 0    

f.close()
