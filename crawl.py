import requests
from bs4 import BeautifulSoup
import bs4
import re
import json
import os
import traceback

# cookie = "username=njames741; eXbD_e8d7_lastvisit=1511319281; eXbD_e8d7_sendmail=1; eXbD_e8d7_sid=uzm18i; eXbD_e8d7_lastact=1511322943%09member.php%09logging; eXbD_e8d7_auth=7d8eL6qixdAkAIiPbiLL348tMgvZu5988i1FD71OWBEcUtFFBCNC43Zni940wexFFykLXVXHWwFHfoVk%2BtBo93c0xBcRuA"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
# response = requests.get("https://ck101.com/thread-4236216-1-1.html",headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')
# text = soup.find('table', id='pid109150798')
# text = text.find('td', class_='t_f')


start = 0
for i in range(1,25): #完本小說總目錄
	url = "https://ck101.com/forum.php?mod=forumdisplay&fid=3419&typeid=2400&typeid=2400&filter=typeid&page="+str(i)
	response = requests.get(url,headers=headers)
	soup = BeautifulSoup(response.text, 'html.parser')
	text = soup.findAll('tbody', class_='threadrow')
	novelAttributesList = {}
	for t in text:  #完本小說每一頁標題目錄
		try:
			title = t.find('div', class_='blockTitle')
			novelURL = title.findAll('a', href=True)
			novelURL = novelURL[1]['href']
		except Exception as e:
			traceback.print_exc()
			continue

		if title.find('h2').text == "全篇小說排行榜":
			continue
		# print(title.text)
		title = title.text.replace("\n","")
		print(title)
		title = re.split(r'[　<>＜＞［］｛｝〔〕『』〈〉《》「」()（）【】 :：\[\]]',title)
		title = [i for i in title if i != ""]
		print(title)
		print(novelURL) 


		if title[1] != "傳統武俠":
			continue

		#判斷標題，作者的前一個詞就是書名，後一個詞就是作者名
		for i in range(0,len(title)):
			if title[i] == "作者":
				book = title[i-1]
				author = title[i+1]

		#續寫
		# if title[2] == "召喚千軍":
		# 	start = 1
		# 	continue
		# if start ==  0:
		# 	continue

		#處理pgNumber是1，導致沒有頁數的tag
		try:
			pg = t.find('span', class_='tps').findAll('a')[-1]
			pgNumber = int(pg.text)
		except Exception as e:
			traceback.print_exc()
			pgNumber = 1
		# print(pg.text)
		# response2 = requests.get(novelURL,headers=headers)
		# soup2 = BeautifulSoup(response2.text, 'html.parser')
		# pg = soup2.find('div', class_='pg').findAll('a')[-2]
		# print(pg.text)
		novelContentList = []

		for j in range(1,pgNumber+1):	#某本小說總頁數   int(pg.text)+1
			# novelURLList = novelURL.split('-')
			# pgURL = novelURL[:-8]+str(j)+novelURL[-7:]
			# pgURL = novelURLList[0]+'-'+novelURLList[1]+'-'+str(j)+'-'+novelURLList[3]
			pgURL = novelURL + "&page=" + str(j)
			print(pgURL)
			response2 = requests.get(pgURL,headers=headers)
			soup2 = BeautifulSoup(response2.text, 'html.parser')
			text2 = soup2.findAll('div', class_='plhin')
			for k in text2:   #某本小說某頁的每層樓
				# print(k.text)
				try:
					content = k.find('td', class_='t_f')
					# unwanted = content.find('i', class_='pstatus')
					# unwanted.extract()
					text = []
					ischapter = 1
					for x in content:
						if isinstance(x, bs4.element.NavigableString):
							# if ischapter == 1:
							# 	ischapter = 0
							# 	continue
							temp = str(x.strip())
							if len(temp) < 20 and ("章" in temp or "回" in temp or "卷" in temp):
								continue
							text.append(x.strip())
					text2 = "".join(text)
					# print(content.text[80:100])
					# print("*************************************************************************************************************")
					# print(content.text.replace(" ",""))
					novelContentList.append(text2.replace(" ",""))
				except Exception as e:
					traceback.print_exc()
			if j == 5:
				break

		del novelContentList[0]
		novelAttributesList = { "書名" : book,
								"作者" : author,
								"內容" : novelContentList}

		# allNovelList.append(novelAttributesList)
		path = title[0]
		if not os.path.isdir(path):
			os.mkdir(path)
			with open(path+"/result.json",'w') as load_f:
				allNovelList = []
				allNovelList.append(novelAttributesList)
				json.dump(allNovelList, load_f, ensure_ascii=False)
		else:
			with open(path+"/result.json",'r') as load_f:
				load_dict = json.load(load_f)

			load_dict.append(novelAttributesList)

			with open(path+"/result.json",'w') as dump_f:
				json.dump(load_dict,dump_f, ensure_ascii=False)
