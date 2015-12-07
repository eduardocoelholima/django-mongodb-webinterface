from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render, render_to_response 
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils.encoding import smart_str

from pymongo import MongoClient

from bson.objectid import ObjectId
import bson

client = MongoClient('ec2-52-27-233-131.us-west-2.compute.amazonaws.com', 27017)
db = client.users
dbname = db._Database__name
collection = db.tweets
collname = collection.collection._Collection__name

def index(request):
	context = None
	template = loader.get_template('polls/index.html')
	resultsStr = ''
	username = ''
	next = ''
	tweetbody = ''
	totalsize = 0
	
	if request.method == 'POST':
		
		if 'comments' in request.POST.keys():
			id = request.POST['id']
			collection.update({'_id':ObjectId(id)},{'$set':{"comment":request.POST['comments']}})
				
		if 'nextvalue' in request.POST.keys():
			next = int(request.POST['nextvalue'])
		else:
			next = 0
		
		if 'username' in request.POST.keys() and 'tweetbody' in request.POST.keys():
			username = request.POST['username']
			tweetbody = request.POST['tweetbody']

			limitval = 15
			results = collection.find({'text':{"$regex":'.*'+str(tweetbody)+'.*'},'fromUser':{"$regex":'.*'+str(username)+'.*'}})
			
			totalsize = results.explain()['n']
			totalpages = totalsize//15 + 1
			
			results.skip(next*limitval).limit( limitval )
			resultsStr += '<table>'
			
			for result in results:
				text     = result['text']
				text 	 = text.replace("'","\ ")
				text 	 = text.replace('"','\ ')
				resultid = str(result['_id'])
				fromUser = str(result['fromUser'])
				
				injectedHTML = '<table>'
				injectedHTML += ' <tr><td>Tweet ID:</td><td>'+str(result['_id'])+'</td></tr>'
				injectedHTML += '<tr><td>User Name:</td><td>'+result['fromUser']+'</td></tr>'
				injectedHTML += '<tr><td>Tweet Text:</td><td>'+text+'</td></tr>'
				injectedHTML += '<tr><td>Latitude:</td><td>'+str(result['latitude'])+'</td></tr>'
				injectedHTML += '<tr><td>Longitude:</td><td>'+str(result['longitude'])+'</td></tr>'
				injectedHTML += '<tr><td>Tweeted At:</td><td>'+result['createdAt']+'</td></tr>'
				
				if 'comment' in result.keys():
					comments = result['comment']
					comments = comments.replace("'","\ ")
					comments = comments.replace('"','\ ')
				else:
					comments = ''
				
				injectedHTML += '<tr><td>Comments: </td><td>'+comments+'</td></tr>'
				injectedHTML += '<tr><td><button name=&quot;addcomment&quot; type=&quot;submit&quot;>Add Comment</button></td><td><input type=&quot;text&quot; name=&quot;comments&quot; value=&quot; &quot;></td></tr>'
				injectedHTML += '</table>'
				injectedHTML += '<button type = &quot;button&quot; onclick=linktogooglemaps(&quot;'+str(result['latitude'])+','+ str(result['longitude'])+'&quot;); class=&quot;buttons&quot;>Google Map Location</button>'
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;id&quot; value=&quot;'+str(result['_id'])+'&quot;/>'
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;username&quot; value=&quot;'+username+'&quot;/>'
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;tweetbody&quot; value=&quot;'+tweetbody+'&quot; />'
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;nextvalue&quot; value=&quot;'+str(next)+'&quot; />'
								
				button 		  = '''<button type = "" onclick="getElementById('tweetdisplay').innerHTML = ' ''' +injectedHTML+''' ' ;show();">View Tweet</button> '''

				resultsStr   += "<tr><td>" + button+ "</td><td>" + str(result['fromUser']) + "</td><td>" + str(result['createdAt']) + "</td></tr>"
				
				
				
			resultsStr += '</table>'
			
			if next != 0:
				resultsStr += '<form id="results" name="resultsform" action="/" method="post"><button name="nextvalue" type="submit" value="'+str(next-1)+'">Previous</button>'
			if next+1 != totalpages:
				resultsStr += '<form id="results" name="resultsform" action="/" method="post"><button name="nextvalue" type="submit" value="'+str(next+1)+'">Next</button>'
			
			if totalsize != 0:
				resultsStr += '<span>&nbsp;&nbsp;&nbsp;&nbsp;' +str(next+1) + ' out of '+ str(totalpages)+ '</span>'
			else:
				resultsStr +=  'No results available'
			resultsStr += '<input type="hidden" name="username" value="'+username+'"/>'
			resultsStr += '<input type="hidden" name="tweetbody" value="'+tweetbody+'" />'
			
			context = RequestContext(request, {'resultsStr': resultsStr,})
	
	#injecting the searchbox, prepopulated with text if avaible
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
	
	params = {"resultsStr":resultsStr, "client":str(client.address),'searchbox':searchbox,'totalsize':totalsize,'dbname':dbname,'collname':collname}

	if resultsStr == '':
		return render_to_response("polls/index.html",params, context_instance=RequestContext(request))
	else:
		return render_to_response("polls/index.html",params, context_instance=RequestContext(request))

