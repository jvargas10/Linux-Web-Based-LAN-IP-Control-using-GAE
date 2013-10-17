#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import re
import logging
import json

from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

classrooms = ["Classroom1","Classroom2","Classroom3","Lab1"]

def createJson(self,ips):
	self.response.headers['Content-Type'] = "application/json; charset= utf-8"
	if ips:
		self.response.out.write(ips)
	else: 	self.response.out.write("Error")

def get_computer_id_from_url(self):
	url = self.request.url.split('/')
	return re.findall(r'[0-9]+',url[-1])[0]


def update_computer(computer_id, actual_computer, new_computer_dict2):
	actual_computer_dict1 = db.to_dict(actual_computer)
	flag = False

	for p in new_computer_dict2: 
		if p == 'cpu' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.cpu = new_computer_dict2[p]
			flag = True
			continue
		if p == 'memory' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.memory = new_computer_dict2[p]
			flag = True
			continue
		if p == 'hdd' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.hdd = new_computer_dict2[p]
			flag = True
			continue
		if p == 'ip' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.ip = new_computer_dict2[p]
			flag = True
			continue
		if p == 'ip_state' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.ip_state = new_computer_dict2[p]
			flag = True
			continue
		if p == 'computer_name' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.computer_name = new_computer_dict2[p]
			flag = True
			continue
		if p == 'motherboard_model' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.motherboard_model = new_computer_dict2[p]
			flag = True
			continue
		if p == 'gpu_model' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.gpu_model = new_computer_dict2[p]
			flag = True
			continue
		if p == 'operative_system' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.operative_system = new_computer_dict2[p]
			flag = True
			continue
		if p == 'installed_programs' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.installed_programs = new_computer_dict2[p]
			flag = True
			continue
		if p == 'computer_location' and actual_computer_dict1[p] != new_computer_dict2[p]: 
			actual_computer.computer_location = new_computer_dict2[p]
			flag = True
			continue

	if flag: 
		k = actual_computer.put()
		if k: 
			memcache.set('computer_entry'+computer_id, actual_computer)
			create_table_computers_content(classrooms, True)
			return True

def change_ip_state(state):
	return int(not state)

def create_computer(self, computer_dict):
	new_entry = Computer(computer_name = computer_dict['computer_name'],
						 ip = computer_dict['ip'] ,
						 ip_state = int(self.request.get('ip_state')),
						 cpu = float(computer_dict['cpu']),
						 motherboard_model = computer_dict['motherboard_model'],
						 hdd = float(computer_dict['hdd']),
						 memory = float(computer_dict['memory']),
						 gpu_model = computer_dict['gpu_model'],
						 operative_system = computer_dict['operative_system'],
						 installed_programs = computer_dict['installed_programs'],
						 computer_location = self.request.get('computer_location'))
	return new_entry.put()

def create_table_computers_content(classrooms, update = False):
	table_content = memcache.get('table_content')
	if table_content is None or update == True:
		table_content = ''
		for classroom in classrooms:
			classroom_computers = list(db.GqlQuery("Select * from Computer where computer_location='%s' order by ip" % classroom))
			total_computers_in_classroom = len(classroom_computers)
			if total_computers_in_classroom == 0: total_computers_in_classroom = 1
			table_content += "<tr valign='center' align='center'><td rowspan='%d'>%s</td>" % (total_computers_in_classroom, classroom)
			for key,computer in enumerate(classroom_computers):
				computer_id = computer.key().id()
				state_img = 'on.png' if computer.ip_state == 1 else 'off.png'
				if key != 0: table_content += '<tr align="center">'
				table_content += 	""" <td><input type='checkbox' name='chk' value='%d'></td>
										<td><img src='/images/%s' width='39px' height='63px'></td>
										<td>%s</td>
										<td><a id= "a-ip" href="http://192.168.1.1/ip-tools/ping_ip.php?ip=%s">%s</a></td>
										<td><a id='a_update' href='/update_computer/%d'>Update</a></td>
										<td><a id='a_delete' href='/delete_computer/%d'>Delete</a></td></tr>
									""" % (computer_id, state_img, computer.computer_name, computer.ip, computer.ip, computer_id, computer_id)
		memcache.set('table_content', table_content)

	return table_content

def create_empty_computer_dict():
	computer_dict = {}
	for e in Computer.properties():
		if not e in ['created']: computer_dict[e] = ''
	return computer_dict

def validating_computer_data(computer_dict):
	error = False
	error_computer_dict = create_empty_computer_dict()
	
	#Regular Expressions
	ip_re = re.compile(r'^\d{2,3}\.\d{2,3}\.\d{1,3}\.\d{1,3}$')
	cpu_hdd_memory_re = re.compile(r'^[0-9]+\.?[0-9]*$')
	
	for key,value in computer_dict.iteritems():
		if key in ['cpu', 'hdd', 'memory']:
			if not cpu_hdd_memory_re.match(str(value)):
				computer_dict[key] = ''
				error_computer_dict[key] = 'Enter a valid number'
				error = True
		
		elif key == 'ip':
			if not ip_re.match(value):
				computer_dict[key] = ''
				error_computer_dict[key] = 'Enter a valid IP'
				error = True

		elif key == 'computer_name':
			if not re.match(r'^(?:aula|lab)\d{1}pc\d{2}$',value):
				computer_dict[key] = ''
				error_computer_dict[key] = "Enter a valid Computer Name (aulaXpcXX or labXpcXX)"
				error = True

		elif value == '' : 
			error_computer_dict[key] = 'Enter valid data in the field'
			error = True

	return computer_dict, error_computer_dict, error


class Computer(db.Model):
	computer_name = db.StringProperty(required=True)
	ip = db.StringProperty(required=True)
	ip_state = db.IntegerProperty(required=True)
	cpu = db.FloatProperty(required=True)
	motherboard_model = db.StringProperty(required=True)
	hdd = db.FloatProperty(required=True)
	memory = db.FloatProperty(required=True)
	gpu_model = db.StringProperty(required=True)
	operative_system = db.StringProperty(required=True)
	installed_programs = db.TextProperty(required=False)
	computer_location = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_environment.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class CreateComputer(Handler):
	def get(self):
		computer_dict = create_empty_computer_dict()
		error_computer_dict = create_empty_computer_dict()

		self.render('create_computer.html', computer_dict = computer_dict, error_computer_dict = error_computer_dict)

	def post(self):
		computer_dict = create_empty_computer_dict()
		for e in computer_dict:
			computer_dict[e]= self.request.get(e)
		
		computer_dict, error_computer_dict, error = validating_computer_data(computer_dict)
	
		if error:
			self.render('create_computer.html', computer_dict = computer_dict, error_computer_dict = error_computer_dict)
		else:
			k = create_computer(self, computer_dict)
			if k: 
				self.redirect('/')
				create_table_computers_content(classrooms, True)
			else: self.write("Error while saving to the DB. Try it again.")
			

class UpdateComputer(Handler):
	def get(self):
		computer_id = get_computer_id_from_url(self)
		computer = memcache.get('computer_entry'+computer_id)
		
		if computer is None:
			computer = Computer.get(db.Key.from_path('Computer', int(computer_id)))
			if not computer: 
				self.render('error_id.html')
				return
			
			memcache.set('computer_entry'+computer_id, computer)
		
		error_computer_dict = create_empty_computer_dict()
		self.render('update_computer.html', computer_dict = db.to_dict(computer), error_computer_dict = error_computer_dict, computer_id = computer_id)

	def post(self):
		computer_dict = create_empty_computer_dict()
		computer_id = get_computer_id_from_url(self)
		for e in computer_dict:
			if e in ['cpu', 'hdd', 'memory']: computer_dict[e] = float(self.request.get(e))
			elif e == 'ip_state': computer_dict[e] = int(self.request.get(e))
			else: computer_dict[e] = self.request.get(e)
		
		computer_dict, error_computer_dict, error = validating_computer_data(computer_dict)
	
		if error:
			self.render('update_computer.html', computer_dict= computer_dict, error_computer_dict = error_computer_dict)
		else:			
			computer = memcache.get('computer_entry'+computer_id)
			if update_computer(computer_id, computer, computer_dict):
				self.redirect('/')
			else: self.write("<h1 style='margin-left: auto; margin-right: auto; width: 70%;'>To update the database register, please modify at least one property</h1>")

class DeleteComputer(Handler):
	def get(self):
		computer_id = get_computer_id_from_url(self)
		
		#Getting computer in cache
		computer = memcache.get('computer_entry'+computer_id)
		
		#Deleting register
		if computer:
			d = memcache.get('computer_entry'+computer_id).delete()
		else: 
			d = db.delete(db.Key.from_path('Computer', int(computer_id)))
		
		if d is None: 
			memcache.delete('computer_entry'+computer_id)
			create_table_computers_content(classrooms, True)
			self.redirect('/')
		else: self.write('Computer could not be delete it. Try again.')

class MainPage(Handler):
    def get(self):
    	url = self.request.url.split('/')
    	if url[-1].find('.json') != -1: 
    		createJson(self, memcache.get("json_update_ip_state"))
    		memcache.delete("json_update_ip_state")
    	else:		
    		table_content = create_table_computers_content(classrooms)
    		self.render('index.html', table_content = table_content)

    def post(self):
    	selected_computers = self.request.get_all('chk')
    	if selected_computers:
    		ips={}
    		for computer_id in selected_computers:
    			computer = memcache.get('computer_entry'+computer_id)
    			if computer is None:
    				computer_key = db.Key.from_path('Computer',int(computer_id))
    				computer = Computer.get(computer_key)

    			ips[computer.ip] = change_ip_state(computer.ip_state)
   
    			computer.ip_state = change_ip_state(computer.ip_state)
    			computer.put()
    			memcache.set('computer_entry'+computer_id, computer)

    		json_ips = json.dumps(ips)
    		memcache.set('json_update_ip_state' , json_ips)

    		create_table_computers_content(classrooms,True)

    	self.redirect('http://192.168.1.1/ip-tools/changing_ip_status.php')
    
app = webapp2.WSGIApplication([('(?:/(?:\.json)?)', MainPage), ('/new_computer', CreateComputer), ('/update_computer/[0-9]+', UpdateComputer), ('/delete_computer/[0-9]+', DeleteComputer)],
                              debug=True)
