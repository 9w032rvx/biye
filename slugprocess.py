#coding:utf-8
import os
import docker
import time
import threading
from os.path import getsize

runner_id=""

def slugbuild():
	"""build the program in container"""
	f=open("slugprocess.log","a+")
	now=time.strftime('%Y-%m-%d %H:%M:%S')
	print "build the program in slugbuilder"
	f.writelines(now+">>>build the program in slugbuilder\n")
	start=time.time()
	try:
		print "building\n......"
		builder=os.popen("git archive master | docker run -i -a stdin slugbuilder")
		builder_id=(builder.read())[:64]
		os.system("docker wait %s"%builder_id)
		os.system("docker cp %s:/tmp/slug.tgz ."%builder_id)
		os.system("docker cp %s:/tmp/slugbuilder.log ."%builder_id)
		end=time.time()
		now=time.strftime('%Y-%m-%d %H:%M:%S')
		f.writelines(now+">>>cost time:%f s\n"%(end-start))
		f.writelines(now+">>>the size after build:%d m\n"%(getsize("slug.tgz")/(1000*1000)))
		f.close()
		print "build completed!"
	except Exception,e:
		f.writelines(now+">>>"+e+"\n")
		f.close()
		print "build failed!"

def slugrun():
	"""run the program in container"""
	print "run the program in slugrunner."
	runner=os.popen("cat slug.tgz | docker run -i -a stdin slugrunner start web")
	global runner_id
	runner_id=(runner.read())[:64]

def containercommit(imgname):
	"""commit the image"""	
	print "create and commit the image."
	count=0
	while True:
		count+=1
		global runner_id
		cid=runner_id
		client=docker.Client(base_url='unix://var/run/docker.sock',version='1.21',timeout=10)
		log=client.logs(container=cid,stdout=True,stderr=True)
		if log.find("Running on http://0.0.0.0:5000/")>0:
			print "the count of checking:",count
			print "successful: "+log
			f=open("slugprocess.log","a+")
			now=time.strftime('%Y-%m-%d %H:%M:%S')
			f.writelines(now+">>>the count of checking:%d\n"%count)
			f.writelines(now+">>>"+log)
			try:
				os.system("docker commit %s %s"%(cid,imgname))
				now=time.strftime('%Y-%m-%d %H:%M:%S')
				f.writelines(now+">>>commit successful!\nTag:%s \tID:%s\n"%(imgname,cid))
				print "commit successful!"
			except Exception,e:
				now=time.strftime('%Y-%m-%d %H:%M:%S')
				f.writelines(now+">>>commit failed:"+e+"\n")
			try:
				now=time.strftime('%Y-%m-%d %H:%M:%S')
				os.system("docker stop %s"%cid)
				f.writelines(now+">>>stop slugrunner successful!\n")
				print "kill the container completed!"
			except Exception,e:
				now=time.strftime('%Y-%m-%d %H:%M:%S')
				f.writelines(now+">>>kill slugrunner failed:"+e+"\n")
			f.close()
			break
	time.sleep(3)
def containersave(image_name):
	print "save the image file."
	f=open("slugprocess.log","a+")
	now=time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		client = docker.Client(base_url='unix://var/run/docker.sock',,timeout=3)
		image = client.get_image(image_name)
		image_tar = open(image_name+'.tar','w')
		image_tar.write(image.data)
		image_tar.close()
	except Exception,e:
		print Exception,":",e   

if __name__ == '__main__':
	# slugbuild()
	# slugrun()
	# containercommit("test_app")
	containersave("test_app")