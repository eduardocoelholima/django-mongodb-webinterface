
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render, render_to_response 
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils.encoding import smart_str

from pymongo import MongoClient

from bson.objectid import ObjectId
import bson


#set mongo client to e c2 instance and the collection to tweets for this assingment
client = MongoClient('ec2-52-27-233-131.us-west-2.compute.amazonaws.com', 27017)
db = client.users
dbname = db._Database__name
collection = db.tweets
collname = collection.collection._Collection__name


#loading the index 
def index(request):
	context = None
	template = loader.get_template('polls/index.html')
	resultsStr = 'No results available.'
	username = ''
	next = ''
	tweetbody = ''
	totalsize = 0
		
	if request.method == 'POST':
		#sets variables based on the request post keys	
		if 'comments' in request.POST.keys():
			id = request.POST['id']
			collection.update({'_id':ObjectId(id)},{'$set':{"comment":request.POST['comments']}})
				
		if 'nextvalue' in request.POST.keys():
			next = int(request.POST['nextvalue'])
		else:
			next = 0
		
		#when username and tweetbody are passed ie search we run mongo query and fetch results
		if 'username' in request.POST.keys() and 'tweetbody' in request.POST.keys():
			username = request.POST['username']
			tweetbody = request.POST['tweetbody']
	
			username = username.strip()
			tweetbody = tweetbody.strip()
			
			limitval = 15
			if username == '' and tweetbody == '':
				query = {}
				
			elif username == '':
				query = {'text':{"$regex":'.*'+str(tweetbody)+'.*'}}
			
			elif tweetbody == '' :
				query = {'fromUser':{"$regex":'.*'+str(username)+'.*'}}
			else:
				query = {'text':{"$regex":'.*'+str(tweetbody)+'.*'},'fromUser':{"$regex":'.*'+str(username)+'.*'}}
			
			results = collection.find(query)
			totalsize = results.explain()['n']
			totalpages = totalsize//15 + 1
			
			#used skip and limit to limit searches and have pages of results
			results.skip(next*limitval).limit( limitval )
			resultsStr = '<table>'
			
			#obtain the results and build an html tables to inject into the display tweet when user clicks "View Tweet" div in index.html file
			for result in results:
				if 'text'  in result and 'fromUser' in result:
					
				
					text     = result['text']
					text 	 = text.replace("'","\ ")
					text 	 = text.replace('"','\ ')
					resultid = str(result['_id'])
					fromUser = str(result['fromUser'])
					injectedHTML  = '<form id= &quot;comments&quot; name= &quot;comments&quot; action= &quot;/&quot; method=&quot;post&quot;p>'
					injectedHTML += '<table>'
					injectedHTML += ' <tr><td>Tweet ID:</td><td>'+str(result['_id'])+'</td></tr>'
					injectedHTML += '<tr><td>User Name:</td><td>'+result['fromUser']+'</td></tr>'
					injectedHTML += '<tr><td>Tweet Text:</td><td>'+text+'</td></tr>'
					injectedHTML += '<tr><td>Latitude:</td><td>'+str(result['latitude'])+'</td></tr>'
					injectedHTML += '<tr><td>Longitude:</td><td>'+str(result['longitude'])+'</td></tr>'
					injectedHTML += '<tr><td>Tweeted At:</td><td>'+result['createdAt']+'</td></tr>'
				
					#if there is comment then display comment else display nothing
					if 'comment' in result.keys():
						comments = result['comment']
						comments = comments.replace("'","\ ")
						comments = comments.replace('"','\ ')
					else:
						comments = ''
				
					injectedHTML += '<tr><td>Comments: </td><td>'+comments+'</td></tr>'
				
					#button for displaying comment
					injectedHTML += '<tr><td><button name=&quot;addcomment&quot; type=&quot;submit&quot;>Add Comment</button></td><td><input type=&quot;text&quot; name=&quot;comments&quot; value=&quot; &quot;></td></tr>'
					injectedHTML += '</table>'
					injectedHTML += '<button type = &quot;button&quot; onclick=linktogooglemaps(&quot;'+str(result['latitude'])+','+ str(result['longitude'])+'&quot;); class=&quot;buttons&quot;>Google Map Location</button>'
				
					#hidden post values 
					injectedHTML += '<input type=&quot;hidden&quot; name=&quot;id&quot; value=&quot;'+str(result['_id'])+'&quot;/>'
					injectedHTML += '<input type=&quot;hidden&quot; name=&quot;username&quot; value=&quot;'+username+'&quot;/>'
					injectedHTML += '<input type=&quot;hidden&quot; name=&quot;tweetbody&quot; value=&quot;'+tweetbody+'&quot; />'
					injectedHTML += '<input type=&quot;hidden&quot; name=&quot;nextvalue&quot; value=&quot;'+str(next)+'&quot; />'
								
					#view tweet button with injected html to propegate to tweetdisplay div onclock
					button 		  = '''<button type = "" onclick="getElementById('tweetdisplay').innerHTML = ' ''' +injectedHTML+''' ' ;show();">View Tweet</button> '''
				
					#String that is displayed in result div, view tweet button, fromUser and created AT
					resultsStr   += "<tr><td>" + button+ "</td><td>" + str(result['fromUser']) + "</td><td>" + str(result['createdAt']) + "</td></tr>"
				
				
				
			resultsStr += '</table>'
			#limited the number of search to speed up searches of large query, next and previous go through pages of results
			if next != 0:
				resultsStr += '<form id="results" name="resultsform" action="/" method="post"><button name="nextvalue" type="submit" value="'+str(next-1)+'">Previous</button>'
			if next+1 != totalpages:
				resultsStr += '<form id="results" name="resultsform" action="/" method="post"><button name="nextvalue" type="submit" value="'+str(next+1)+'">Next</button>'
			
			
			
			#if totalsize of search was 0 ie no result found show now result otherwise show the numer of page out of all pages
			if totalsize != 0:
				resultsStr += '<span>&nbsp;&nbsp;&nbsp;&nbsp;' +str(next+1) + ' out of '+ str(totalpages)+ '</span>'
			else:
				resultsStr +=  'No results available'
			resultsStr += '<input type="hidden" name="username" value="'+username+'"/>'
			resultsStr += '<input type="hidden" name="tweetbody" value="'+tweetbody+'" />'
			#resultsStr += '</form>'
			
			
			context = RequestContext(request, {'resultsStr': resultsStr,})
	
	#injecting the searchbox, prepopulated with text if availble, this is used so that username and tweetbody are persisted through all of our post request unless set
	searchbox = '''<label for="username">Search by User: </label>
					<input type="text" id="username" name="username" autocomplete="on" value ="''' 
	searchbox += str(username)			
	searchbox += '''" size="25"/><br/><br/>
					<!--span>Search by Time/Date of Tweet:&nbsp;&nbsp;&nbsp;</span>
					<label for="starttime">Start: </label>
					<input type="text" id="starttime" name="starttime" size="18"/>
					<label for="stoptime">&nbsp;&nbsp;&nbsp;Stop: </label>
					<input type="text" id="stoptime" name="stoptime" size="18"/><br/>
					</br-->
					<label for="tweetbody">Search by Tweet Content:</label>
					<input type="text" id="tweetbody" name="tweetbody" value = "'''
	searchbox += str(tweetbody)				
	searchbox +=	'''" autocomplete="on" size="65"/><br/><br/>
					<input type='hidden' name='csrfmiddlewaretoken' value='{{csrf_token}}'>
				</div><!-- end formfeild   -->
				<div id="buttonfeild">
					<input type="hidden" name="csrfmiddlewaretoken" value="pHK2CZzBB323BM2Nq7DE2sxnQoBG1jPl" disabled="">
					<input type="submit" value="Search" class="buttons"/>
					<button type = "button" class="buttons" onclick="reload();">Reset</button>'''
					#<button type = "button" class="buttons" onclick="resetTest()">Reset</button>'''
	
	#passing python object parameters to the template file(index)
	params = {"resultsStr":resultsStr, "client":str(client.address),'searchbox':searchbox,'totalsize':totalsize,'dbname':dbname,'collname':collname}
	
	#if resultsStr == '':
	return render_to_response("polls/index.html",params, context_instance=RequestContext(request))
	#else:
	#	return render_to_response("polls/index.html",params, context_instance=RequestContext(request))

