from django.db import models
from django.contrib.auth.models import User
import hashlib
import datetime
import time
import os

#
# A user can possess many attributes that define their auth
# An attribute can belong to many users
#
# A document can possess many attributes that define its necessary auth
# An attribute can belong to many documents
#

def content_file_name(instance, filename):
	DATE_FORMAT = "%Y-%m-%d" 
	TIME_FORMAT = "%H-%M-%S"
	ext = os.path.splitext(filename)
	ext = ext[1].encode('ascii', 'ignore')

	date_time = datetime.datetime.now()
	date_time_string = date_time.strftime("%s-%s" % (DATE_FORMAT, TIME_FORMAT))
	new_name = filename + date_time_string
	hash_string = hashlib.md5(new_name).hexdigest()

	date_string = datetime.date.today().strftime("%s" % DATE_FORMAT)
	return 'files/' + date_string + '/%s%s' % (hash_string, ext)

class Document(models.Model):
	fileName = models.CharField(max_length=100)
	fileRef = models.FileField(upload_to=content_file_name)

	def __unicode__(self):
		return self.fileName

class RWAttribute(models.Model):
	identifier = models.CharField(max_length=50)
	users = models.ManyToManyField(User, blank=True)
	documents = models.ManyToManyField(Document, blank=True)

	def __unicode__(self):
		return self.identifier