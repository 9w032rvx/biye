#coding:utf-8
import os
import docker
import time
import threading
from os.path import getsize
import pexpect
import sys

class get_tar():
	def __init__(self,path,name,show_log=False):
		self.result = {"error":None,"error message":None,"work":False}
		self.task_id = path[len(path)-37:-1]
		self.short_id = self.task_id[:8]
		
		os.chdir(path)
		self.file_obj =open("progresslog-" + self.short_id,"w")
		self.path = path
		self.container_id=None
		self.name = name

		#print log info or not
		self.show_log = show_log

		# the minimum size of the slugfile in B
		self.min_slug=1024
	def log (self,cmd,):
		cmd = self.get_time()+">>>"+cmd+"\n"
		self.file_obj.write(cmd)
		if self.show_log:
			cmd = cmd[:-1]
			print cmd
	def get_time(self):
		return str(time.strftime('%Y-%m-%d %H:%M:%S'))
	def dockerapi(self,base_url='unix://var/run/docker.sock',version='1.21',timeout=10):
		try:
			client = docker.Client(base_url,version,timeout)
			return client
		except Exception,e:
			self.result["error"] = "create api failed"
			self.result["error message"] = e
			self.log(str(self.result))
			self.file_obj.close()
			return e

	def slug_builder(self,client):
		self.log("\t"+ self.path)
		self.log("start building slug")
		builder = os.popen("git archive master | docker run -i -a stdin slugbuilder")
		container_id = (builder.read())[:64]
		client.wait(container_id)


		#copy the files out and rename them
		os.system("docker cp "+container_id+":/tmp/slug.tgz "+self.short_id+".tgz")
		os.system("docker cp "+container_id+":/tmp/slugbuilder.log buildlog-"+self.short_id)
		line = "retrive complete. slug size:%d MB"%(getsize(self.short_id+".tgz")/(1000*1000))
		self.log(line)
	 	self.container_id = container_id
		try:
		 	client.remove_container(self.container_id)
		except Exception,e:
			self.result["error"] = Exception
			self.result["error message"] = e
			self.log(str(self.result))
			self.file_obj.close()
		 	return e
		 	#check if the files are too small
	 	if (getsize(self.short_id+".tgz")<=self.min_slug):
	 		self.result["error"] = "slug building seems failed"
	 		self.result["error message"] = "slug file file is too small"
	 		self.log(self.result["error message"])
	 		self.log("slug:"+getsize(self.short_id+".tgz"))
	 		self.log("logfile:"+getsize("buildlog-" + self.short_id))
	 		self.file_obj.close()
	 		return
		 	
		


	def slug_runer(self):
		self.log("start runing the slug")
		cmd = "cat "+self.short_id+".tgz | docker run -i -a stdin slugrunner start web"
		runner=os.popen(cmd)
		self.container_id=(runner.read())[:64]
	def commit(self,client):
		#check if the container is runing
		flag = False
		all_runing_containers = client.containers()
		for container in all_runing_containers:
			if container["Id"] == self.container_id:
				self.log("status of container:"+container["Status"])
				flag = True
				break
		if not flag:
			self.log("container is not runing")

		#viod name(tag) conflict
		if len(client.images(name=self.name))>0:
			self.name += self.get_time()

		#commit the container to image	
		self.log("start committing the container")
		client.commit(container=self.container_id,tag=self.name)
		self.log("commit compelete tag:\t"+self.name)
		#do some cleaning job
		client.remove_container(self.container_id,force=True)

	def save(self,client):
		try:
			self.log("start saving the tarfile")
			image = client.get_image(self.name)
			image_tar = open(image_name+'.tar','w')
			image_tar.write(image.data)
			image_tar.close()
			self.log(" save compelete")
			client.remove_image(tag=self.name,force=True)
		except Exception,e:
			self.result["error"] = Exception
			self.result["error message"] = e
			self.log(str(self.result))
			self.file_obj.close()  
	def mian(self):
		client = self.dockerapi()
		if not self.result["error"] == None:
			return self.result

		self.slug_builder(client)
		if not self.result["error"] == None:
			return self.result

		self.slug_runer()
		self.commit(client)
		if not self.result["error"] == None:
			return self.result
		self.log("all done")
		self.result["work"] = True
		self.file_obj.close()
		return self.result

if __name__ == '__main__':
	get_tar = get_tar(sys.argv[1],sys.argv[2],show_log=True)
	print get_tar.mian()