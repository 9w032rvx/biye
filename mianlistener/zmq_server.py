#coding=utf8
import zmq
import json
import traceback
import pexpect
import os,runpy
from settings import zmqAddress,repoPath
# from gittle import Gittle
def gitClone(gitUrl,passwd):
	try:
		# gitUrl = '''git@172.29.152.251:/var/www/html/sky/repo/d7205e12-f169-11e5-ba32-70e2840d7ded.git'''
		cmd = "git clone " + gitUrl
		print cmd
		child = pexpect.spawn(cmd,timeout=10)
		# 处理前置事件知道发送密码
		i = child.expect (['no\)?', 'password:', 'exists'])
		if i==0:
			child.sendline ('yes')
			child.expect ('password:')
			child.sendline (passwd)
		elif i==1:
			child.sendline (passwd)
		elif i==2:
			print('not empty')
			return {"code":1,"message":"仓库已存在"}
		# 获取发送密码后的状态
		i = child.expect (['denied', 'done',])
		print child.before
		print child.after
		if i==0:
			return {"code":2,"message":"密码错误"}
		elif i==1:
			child.expect(pexpect.EOF)
			print child.before
			return {"code":0,"message":"OK"}
	except:
		traceback.print_exc()
		exit(1)
		return {"code":3,"message":"超时"}
if __name__ == '__main__':
	test_data = {u'cmdType': u'create', u'id': u'33', 
	u'gitUrl': u'git@172.29.152.251:/var/www/html/sky/repo/d7205e12-f169-11e5-ba32-70e2840d7ded.git', u'gitPasswd': u'git'}
	# print gitClone(test_data['gitUrl'],test_data['gitPasswd'])
	message = test_data
	path = message['gitUrl'][:-4]
	path = path[len(path)-36:]
	cmd = "cp slugprocess.py " + path + " " + name
	child = pexpect.spawn(cmd,timeout=10)
	# runpy.run_path('hello.py')
	# try:
	# 	context = zmq.Context()
	# 	socket = context.socket(zmq.REP)
	# 	socket.bind(zmqAddress)
	# 	print "ZMQ正在监听%s" %(zmqAddress)
	# except:
	# 	traceback.print_exc()
	# 	exit(1)
	# while True:
	# 	message = socket.recv()
	# 	message = json.loads(message)
	# 	print "Received request: ", message
	# 	if 'create' == message['cmdType']:
	# 		response = {}
	# 		try:
	# 			# response = gitClone(message['gitUrl'],message['gitPasswd'])
	# 			path = message['gitUrl'][:-4]
	# 		except:
	# 			response['code'] = 4
	# 			response['message'] = "Clone内部错误"
	# 	print response
	# 	socket.send(json.dumps(response))
