from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from fileaccess.forms import *
from fileaccess.models import *
from django.core.servers.basehttp import FileWrapper
import os, mimetypes

# Default index - we come here at first always, unless user is auth'ed
# This will handle the login form easily before moving on
# If we come to the login method and are authenticated, forward to file list
# Otherwise, we create a username and password, and try to authenticate
# If we can authenticate, then we go to the right place. If not, we don't go anywhere
def login_user(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/fileaccess/view_files/")

	if request.method == "POST":
		form = AccessLoginForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)

			if user is not None and user.is_active:
				login(request, user)
				return HttpResponseRedirect("/fileaccess/view_files/")
	else:
		form = AccessLoginForm()

	return render(request, 'fileaccess/index.html', {
		'form' : form,
	})


# Simple function to log user out when they want
# Uses Django's easy authentication system to logout
def logout_user(request):
	logout(request)
	return HttpResponseRedirect('/fileaccess/')


# Method that checks whether a user's attributes give them access
# to a file specified in the document argument
def user_has_access(user_attrs, document):
	doc_att = document.rwattribute_set.all()
	remain = list(set(doc_att) - set(user_attrs))
	if not remain:
		return True

	return False

# Default page to view files in a list that the user has access to
# This is simple, but we must filter based on the user's attributes
# So we should create a list of documents that the user can access
# Before sending it to the server. Hooray!
def view_files(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/fileaccess/')

	documents = Document.objects.all()
	user_att = request.user.rwattribute_set.all()
	docs_avail = []

	# Loop, get doc atts; compare to the user atts
	# If no atts remain after set operations, we can manipulate file
	for doc in documents:
		if user_has_access(user_att, doc):
			docs_avail.append(doc)

	context = {'documents' : docs_avail}
	return render(request, 'fileaccess/file_list.html', context)


# This function allows us to add a new file quickly and efficiently.
# We create a document with a filename and file object. We then need
# to save it before adding attributes. Once it is saved, we link
# the selected attributes to the document object. For reference,
# anytime we also create a user we must make sure to go into the 
# attributes and add them for new users!
def new_file(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/fileaccess/')

	if request.method == "POST":
		form = NewFileForm(request.POST, request.FILES)

		if form.is_valid():
			fileName = form.cleaned_data['fileName']
			fileRef = form.cleaned_data['fileUpload']
			document = Document(fileName=fileName, fileRef=fileRef)
			document.save()

			choices = form.cleaned_data['attributes']
			for choice in choices:
				anAttr = RWAttribute.objects.get(id=choice)
				anAttr.documents.add(document)

			return HttpResponseRedirect("/fileaccess/view_files/")
	else:
		form = NewFileForm()

	return render(request, 'fileaccess/new_file.html', {
		'form' : form,
	})


# Download file method - makes sure user is authenticated and has
# access to this document. If they do have access, we construct a 
# file name and send it back to the browser as an attachment.
def download_file(request, file_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/fileaccess/')

	document = Document.objects.get(id=file_id)
	user_att = request.user.rwattribute_set.all()

	if not user_has_access(user_att, document):
		return HttpResponseRedirect('/fileaccess/')

	file_path = document.fileRef.url
	file_name = os.path.basename(file_path)
	ext = os.path.splitext(file_name)
	ext = ext[1].encode('ascii', 'ignore')
	content_type = mimetypes.guess_type(file_path)[0]

	wrapper = FileWrapper(file(file_path))
	response = HttpResponse(wrapper, content_type=content_type)
	response['Content-Disposition'] = 'attachment; filename=%s%s' % (document.fileName, ext) 
	response['Content-Length'] = os.path.getsize(file_path)
	return response


# Very simple method to delete a given document. We must call delete on the
# FieldFile object first though, as otherwise the file will not be deleted
# from the file system.
def delete_file(request, file_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/fileaccess/')

	document = Document.objects.get(id=file_id)
	document.fileRef.delete()
	document.delete()

	return HttpResponseRedirect('/fileaccess/')


# The very hard method to work with editing files. Developed under the assumption
# that the user can change one thing at a time. We can only populate the form
# with initial values for title and checkbox, so the file field is not required.
# So if no file is chosen, we keep the same file, and if a file is chosen, we over-
# write the old one. We always set the document.fileName, as that value is initialized
# to the form. Likewise, we always remove all old attributes and add new one based on
# what the user has chosen, since they are initialized to what was previous as well.
def edit_file(request, file_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/fileaccess/')

	document = Document.objects.get(id=file_id)
	user_att = request.user.rwattribute_set.all()
	doc_att = document.rwattribute_set.all()

	if not user_has_access(user_att, document):
		return HttpResponseRedirect('/fileaccess/')

	if request.method == "POST":
		form = UpdateFileForm(request.POST, request.FILES)

		if form.is_valid():
			fileName = form.cleaned_data['fileName']
			fileRef = form.cleaned_data['fileUpload']
			choices = form.cleaned_data['attributes']

			document.fileName = fileName

			if fileRef:
				document.fileRef.delete()
				document.fileRef = fileRef

			for old_att in doc_att:
				old_att.documents.remove(document)

			for choice in choices:
				new_att = RWAttribute.objects.get(id=choice)
				new_att.documents.add(document)

			document.save()

			return HttpResponseRedirect("/fileaccess/view_files/")
	else:
		atts = [(att.pk) for att in doc_att]
		initial = {'fileName' : document.fileName, 'attributes' : atts}
		form = UpdateFileForm(initial=initial)

	return render(request, 'fileaccess/edit_file.html', {
		'document' : document,
		'form' : form,
	})

