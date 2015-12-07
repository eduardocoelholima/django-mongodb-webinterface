from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import Question
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from pymongo import MongoClient
from django.shortcuts import render_to_response 
from django.core.context_processors import csrf
from .models import Choice, Question
from django.utils.encoding import smart_str
from bson.objectid import ObjectId

import bson


client = MongoClient('ec2-52-27-233-131.us-west-2.compute.amazonaws.com', 27017)
db = client.users
dbname = db._Database__name
collection = db.tweets
collname = collection.collection._Collection__name

def index(request):
	context = None
	template = loader.get_template('polls/index1.html')
	#results = None
	resultsStr = ''
	username = ''
	next = ''
	tweetbody = ''
	totalsize = 0
	
	if request.method == 'POST':
		if 'username' in request.POST.keys() and 'tweetbody' in request.POST.keys():
			username = request.POST['username']
			tweetbody = request.POST['tweetbody']
	
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

	
	
	if request.method == 'POST':
		
		
		if 'comments' in request.POST.keys():
			#resultsStr += request.POST['id'] + ' '+request.POST['comments']
			id = request.POST['id']
			collection.update({'_id':ObjectId(id)},{'$set':{"comment":request.POST['comments']}})
		
		if 'username' in request.POST.keys() and 'tweetbody' in request.POST.keys():
			username = request.POST['username']
			tweetbody = request.POST['tweetbody']
		
		if 'nextvalue' in request.POST.keys():
			next = int(request.POST['nextvalue'])
		else:
			next = 0
			
		
		if username is not None:
			limitval = 15
			results = collection.find({'text':{"$regex":'.*'+str(tweetbody)+'.*'},'fromUser':{"$regex":'.*'+str(username)+'.*'}})
			
			totalsize = results.explain()['n']
			totalpages = totalsize//15 + 1
			
			results.skip(next*limitval).limit( limitval )
			resultsStr += '<table>'
			
			for result in results:
				text = result['text']
				text = text.replace("'","\ ")
				text = text.replace('"','\ ')
				
				
				resultid = str(result['_id'])
				
				fromUser = str(result['fromUser'])
				
				
				
				#injectedHTML = '<p>'+fromUser+'</p>'
				#injectedHTML += '<p>'+text.replace("'","\ ")+'</p>'
				#injectedHTML += 'Comments: <input type=&quot;text&quot; name=&quot;fname&quot;>'
				
				 
				
				#injectedHTML = '<form id= &quot;comments&quot; name= &quot;comments&quot; action= &quot;/polls/&quot; method=&quot;post&quot;>'''
				injectedHTML = '<table>'
				injectedHTML += ' <tr><td>Tweet ID:</td><td>'+str(result['_id'])+'</td></tr>'
				injectedHTML += '<tr><td>User Name:</td><td>'+result['fromUser']+'</td></tr>'
				injectedHTML += '<tr><td>Tweet Text:</td><td>'+text+'</td></tr>'
				injectedHTML += '<tr><td>Latitude:</td><td>'+str(result['latitude'])+'</td></tr>'
				injectedHTML += '<tr><td>Logitude:</td><td>'+str(result['longitude'])+'</td></tr>'
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
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;id&quot; value=&quot;'+str(result['_id'])+'&quot;/>'
				
				
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;username&quot; value=&quot;'+username+'&quot;/>'
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;tweetbody&quot; value=&quot;'+tweetbody+'&quot; />'
				injectedHTML += '<input type=&quot;hidden&quot; name=&quot;nextvalue&quot; value=&quot;'+str(next)+'&quot; />'
				#injectedHTML
				#injectedHTML += '<button name=&quot;addcomment&quot; type=&quot;submit&quot;>Add Comment</button>'
				#injectedHTML += '<form/>'                                                
                                                                
            		
				
				
				
				button 	= '''<button type = "" onclick="getElementById('tweetdisplay').innerHTML = ' ''' +injectedHTML+''' ' ;show();">View Tweet</button> '''

				resultsStr += "<tr><td>" + button+ "</td><td>" + str(result['fromUser']) + "</td><td>" + str(result['createdAt']) + "</td></tr>"
				
				
				
			resultsStr += '</table>'
			
			if next != 0:
				resultsStr += '<form id="results" name="resultsform" action="/polls/" method="post"><button name="nextvalue" type="submit" value="'+str(next-1)+'">Previous</button>'
			if next+1 != totalpages:
				resultsStr += '<form id="results" name="resultsform" action="/polls/" method="post"><button name="nextvalue" type="submit" value="'+str(next+1)+'">Next</button>'
			
			if totalsize != 0:
				resultsStr += '<span>&nbsp;&nbsp;&nbsp;&nbsp;' +str(next+1) + ' out of '+ str(totalpages)+ '</span>'
			else:
				resultsStr +=  'No results available'
			resultsStr += '<input type="hidden" name="username" value="'+username+'"/>'
			resultsStr += '<input type="hidden" name="tweetbody" value="'+tweetbody+'" />'
			
			context = RequestContext(request, {'resultsStr': resultsStr,})

	

	#for keys in request.POST.keys():
		#resultsStr += str(keys) + ' '
		#resultsStr += request.POST['tweetbody']
		
		
	params = {"resultsStr":resultsStr, "client":str(client.address),'searchbox':searchbox,'totalsize':totalsize,'dbname':dbname,'collname':collname}
	params.update(csrf(request))
	if resultsStr == '':
		return render_to_response("polls/index1.html",params, context_instance=RequestContext(request))
	else:
		return render_to_response("polls/index1.html",params, context_instance=RequestContext(request))




class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'



def vote1(request):
    template = loader.get_template('polls/index1.html')
    if request.method == 'POST':
    	username = request.POST['username']
    	tweetbody = request.POST['tweetbody']
    	results = collection.find({'text':{"$regex":'.*'+str(tweetbody)+'.*'},'fromUser':{"$regex":'.*'+str(username)+'.*'}})
    	resultsStr = ""
    	for result in results:
    		resultsStr += '\n' + str(result)
    	
    	context = RequestContext(request, {
        'resultsStr': resultsStr,
    	})
    	
    	return HttpResponse(template.render(context))
    	

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': request.POST['username'],
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
