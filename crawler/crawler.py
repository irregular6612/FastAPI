import requests
import json

course_url = f"https://zeus.gist.ac.kr/uls/ulsOpenListQ/select.do"

def crawler(url : str, query : str):
    # cookie WMONID
    url1 = "https://zeus.gist.ac.kr/sys/lecture/lecture_open.do"
    # cookie ZSESSIONID
    url2 = "https://zeus.gist.ac.kr/font/NanumGothic.woff2"
    
    session = requests.Session()
    response = session.get(url1)
    print("First response : to get Cookie1\n")
    print(response.headers)
    COOKIE_WMONID = response.cookies.values()[0]    
    
    headers = { "accept":"*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "connection":"keep-alive",
    "cookie": COOKIE_WMONID,
    "host":"zeus.gist.ac.kr",
    "origin":"https://zeus.gist.ac.kr",
    "referer":"https://zeus.gist.ac.kr/sugang.css",
    "sec-ch-ua":'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile":"?0",
    "sec-ch-ua-platform":"macOS",
    "sec-fetch-dest":"font",
    "sec-fetch-mode":"cors",
    "sec-fetch-site":"same-origin",
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    ''''''

    data = {"SSV" : "utf-8",
            "WMONID" : COOKIE_WMONID,
            "univ_clsf_cd" : "USR01.UNIV",
            "yy" : "2024",
            "shtm_cd" : "USR03.20",
            "sust_mj_cd" : "0211",
            "cptn_div_cd" :  "",
            "curs_rech_div_cd": "",
            "cors_detl_div_cd" : "",
            "sbjt_nm" : "",
            "lang_div" : "kor",
            "user_div" : "lec",
            "cncllt_yn" : "N",
            "lt_lang" :  "",
            "pg_key" :  "",
            "page_open_time" : "",
            "page_open_time_on" :  ""
            }
    response = session.post(url)
    '''
    session.headers.update(headers)
    response = session.get(url2)
    '''
    print("\n2nd response : to get Cookie2\n")
    print(response.headers)
    #session.headers.update(headers)
    COOKIE_ZSESSIONID = response.cookies.values()[0]
    
    Cookies = {
        "WMONID" : COOKIE_WMONID,
        "ZSESSIONID" : COOKIE_ZSESSIONID
    }
    #print(response.text)
    
    print("\nCookies\n")
    print(Cookies)
    
    headers = {"accept": "*/*",
    "accept-encoding" : "gzip, deflate, br, zstd",
    "accept-language" : "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "connection" : "keep-alive",
    # "content-length" : "252",
    "content-type" : "text/plain;charset=UTF-8",
    #"cookie" : f"WMONID={COOKIE_WMONID}; ZSESSIONID={COOKIE_ZSESSIONID}",
    "host" : "zeus.gist.ac.kr",
    "origin" : "https://zeus.gist.ac.kr",
    "referer" : "https://zeus.gist.ac.kr/QuickView.html?formname=Lecture::UlsOpenListQ.xfdl",
    "sec-ch-ua" : '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile" : "?0", 
    "sec-ch-ua-platform" : "macOS",
    "sec-fetch-dest" : "empty",
    "sec-fetch-mode" : "cors",
    "sec-fetch-site" : "same-origin",
    "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    print("\nHeaders\n")
    print(headers)
    
    session.headers.update(headers)
    response = session.post(url, json=data, cookies=Cookies)
    print("\nLast response :\n")
    print(response.headers)
    print("\nresopnse: \n")
    #print(response.status_code)
    print(response.content.decode('utf-8'))
    #print(response.cookies.values())
    #print(response2.status_code)
    #print(response2.text)
    return True

crawler(course_url, None)