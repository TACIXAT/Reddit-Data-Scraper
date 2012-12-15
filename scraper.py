#TODO
#celeb csv
#time comments
#time stamp all log entries?
#log function

import os
import re
from time import sleep
import datetime
import urllib2
import urllib
import json
import csv
import copy

#global declares
verbose = True
targetSubreddit = 'pics'
target = "http://www.reddit.com/r/" + targetSubreddit + "/new/.json?sort=new"
posts = {}
comments = {}
kindList = {'t1' : 'comment',
			't2' : 'account',
			't3' : 'link',
			't4' : 'message',
			't5' : 'subreddit'}
monthDays =  [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
labels = ["ID", "User", "Total", "Ups", "Downs", "Link", "OP", "Parent", "Highest", "Depth", "Timestamp", "Celebrity", "Title", "Content"]
currentDate = datetime.datetime.now()
celebList = []

#TODO remove this place holder function
def doSomething():
	return 0

#logger
def logger(fmat, args=None):
	tstamp = datetime.datetime.now()
	tstamp = '[' + str(tstamp)[:19] + '] '
	message = tstamp + fmat + '\n'
	if args == None:
		log.write(message)
	else:
		log.write(message % args)

#set User-Agent
headers = {'User-Agent' : 'scraper bot go far\\Ubuntu 12.04 64\\Python\\user robot_one'}
	
#load or create file
def loadFile(targetDate=datetime.datetime.now(), preExt=""):
	if preExt != "" and preExt[0] != '.':
		preExt = '.' + preExt
	
	sfname = str(targetDate)[:10] + preExt + '.json'
	ffname = './data/' + sfname
	hasMatch = False
	flist = os.listdir('./data')
	
	for item in flist:
		if item == sfname:
			hasMatch = True
			break
	
	if hasMatch:
		if verbose:
			logger('File match found. %s\nLoading json.', (sfname))
		f = open(ffname)
		loaded = json.load(f)
		
		if preExt == "":
			global posts 
			posts = loaded
		elif preExt == ".c":
			global comments
			comments = loaded
	else:
		if verbose:
			logger('No match found.\nCreating file. %s', (sfname))
		f = open(ffname, 'w')
	
	f.close()
	
#open URL
def fetchJSON(URL):
	req = urllib2.Request(URL, None, headers)
	
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		logger("LOAD ERROR: %s\n\t%s", (str(e.code), URL))
		sleep(10)
		return -1
	except urllib2.URLError, e:
		logger("URL ERROR: %s\n\t%s", (str(e.args), URL))
		sleep(10)
		return -1
	
	#if verbose:
		#logger('Response received.')

	jsonpage = json.load(response)
	return jsonpage

#move json into dict posts
def updatePosts(page):
	global celebList
	#if verbose:
		#logger('Adding json page listings to posts object.')
	#print json.dumps(page, indent=4)
	UTCFilter = datetime.datetime(currentDate.year, currentDate.month, currentDate.day).strftime('%s')
	for child in page['data']['children']:
		data = child['data']
		if data['id'] not in posts and int(data['created_utc']) >= int(UTCFilter):
			posts[data['id']] = {
				'ID':data['id'], 
				'User':hash(data['author']), 
				'Total':data['score'], 
				'Ups':data['ups'], 
				'Downs':data['downs'], 
				'Link':True, 
				'OP':True, 
				'Parent':None, 
				'Highest':None, 
				'Depth':None,
				'Timestamp':data['created_utc'],
				'Celebrity':False,
				'Title':None,
				'Content':None}
		elif data['id'] in posts:
			posts[data['id']]['Total'] = data['score'] 
			posts[data['id']]['Ups'] = data['ups']
			posts[data['id']]['Downs'] = data['downs'] 
			if data['ups'] > 49 or hash(data['author']) in celebList:
				posts[data['id']]['Celebrity'] = True
				posts[data['id']]['Title'] = data['title'].encode('ascii','xmlcharrefreplace')
				posts[data['id']]['Content'] = data['url'].encode('ascii','xmlcharrefreplace')
				if hash(data['author']) not in celebList:
					celebList.append(hash(data['author']))
	
#dump json	
def writeFile(date=datetime.datetime.now(), usePosts=True):
	if usePosts:
		sfname = str(date)[:10] + '.json'
		output = posts
	elif not usePosts:
		sfname = str(date)[:10] + '.c.json'
		output = comments

	ffname = './data/' + sfname
	if verbose:
		logger('Writing to file ' + sfname)
	f = open(ffname, 'w')
	f.write(json.dumps(output, indent=4))
	f.close()
	
#print format			
def pageprint():
	widths = [8, 20, 8, 8, 8, 8, 8, 8, 8, 8, 32, 8, 8, 8]
	skipList = [10, 11, 12, 13]
	for i in range(0,len(labels)):
		if i not in skipList:
			print labels[i].rjust(widths[i]),
	print
	
	for key in sorted(posts.keys()):
		for i in range(0,len(posts[key])):
			if i not in skipList:
				print str(posts[key][labels[i]]).rjust(widths[i]),
		print

total = 0

#fetch all the comments
def getComments():
	global total
	commentQ = []
	#for each post
	for entry in posts:
		total = 0
		#make sure it's a post
		if posts[entry]['Link'] == True:
			postURL = "http://www.reddit.com/comments/" + posts[entry]['ID'] + ".json?sort=top&limit=500"
			if verbose:
				logger('Loading comments for %s.', posts[entry]['ID'])
			#fetch as many comments as possible
			postJSON = fetchJSON(postURL)
			count = 0
			while postJSON == -1 or len(postJSON) == 0:
				postJSON = fetchJSON(postURL)
				count += 1
				logger("Retry %d", count)
				if count > 9:
					break
			if count == 10:
				continue
			#update OP
			updatePosts(postJSON[0])
			#separate the comments
			loadedComments = postJSON[1]['data']['children']
			#get id and author
			loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
			loadedName = postJSON[0]['data']['children'][0]['data']['name']
			loadedAuthor = hash(postJSON[0]['data']['children'][0]['data']['author'])
			#initialize the post's comment queue
			commentQ = parsePost(loadedComments, loadedLinkID, loadedAuthor)
			
			if verbose:
				logger('%d comments collected.', total)
				if len(commentQ) > 0:
					logger('Loading more comments for %s.', posts[entry]['ID'])
			#for each in commentQueue, load pages, parsePosts ...
			sleep(4)
			while len(commentQ) > 0:
				start = datetime.datetime.now()
				metaList = commentQ.pop()
				postJSON = getMore(metaList, loadedName, loadedAuthor)
				if postJSON == -1:
					continue

				loadedComments = postJSON[1]['data']['children']
				initialDepth = metaList['depth']
				commentQ += parsePost(loadedComments, loadedLinkID, loadedAuthor, initialDepth)

				finish = datetime.datetime.now()
				delta = finish-start
				if delta.seconds < 2:
					sleep(4-delta.seconds)

				if verbose:	
					logger("%d comments for post %s.", (total, posts[entry]['ID']))
					logger("%d meta comment lists remaining.", len(commentQ))	
		if verbose:	
			logger("%d total comments for post %s.", (total, posts[entry]['ID']))				

def getMore(metaList, linkName, linkAuthor):
	moreObj = metaList['moreObj']
	clist = moreObj['children']
	
	childs = ''
	for ea in clist:
		childs += ea + ','
	childs = childs[:len(childs)-1] #remove comma

	postURL = 'http://www.reddit.com/api/morechildren/.json'	
	values = {'children':childs, 'link_id':linkName, 'id':moreObj['name']}
	data = urllib.urlencode(values)
	req = urllib2.Request(postURL, data, headers)

	response = -1
	while response == -1:
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			logger("LOAD ERROR: %s", str(e.code))
			sleep(4)
			response = -1
		except urllib2.URLError, e:
			logger("URL ERROR: %s", str(e.args))
			sleep(4)
			response = -1

	
	page = json.load(response) #get back crappy jquery flat list
	#logger("%s", page)
	proto = {'kind':'Listing', 'data':{'children':[], 'modhash':"", 'before':None, 'after':None}}
	datar = []	#mock page
	datar.append({'kind':'Listing', 'data':{'children':[{'kind':'t3', 'data':{'id':linkName[3:],'author':linkAuthor,'name':linkName}}]}})
	datar.append({'kind':'Listing', 'data':{'modhash':"", 'children':[], 'before':None, 'after':None}})

	dlookup = {}

	if len(page['jquery']) > 14:
		for entry in page['jquery'][14][3][0]:
		    dlookup[entry['data']['name']] = entry

		for entry in page['jquery'][14][3][0]:
		    pid = entry['data']['parent_id'] 
		    if pid in dlookup:
		        if 'children' not in dlookup[pid]['data']:
		            dlookup[pid]['data']['replies'] = copy.deepcopy(proto)
		        dlookup[pid]['data']['replies']['data']['children'].append(entry)
		    else:
		        datar[1]['data']['children'].append(entry)	
	else:
		datar = -1

	return datar


#parse comments, append 'more' sections to queue					
def parsePost(postComments, parentID, OP, initialDepth=0):
	global total
	toParse = []
	commentQ = []
	toParse.append({'pid':parentID, 'comments':postComments, 'depth':initialDepth})
	#if verbose:
		#logger("Parsing post.")

	while len(toParse) > 0:
		metaChild = toParse.pop()
		cList = metaChild['comments']
		while len(cList) > 0:
			child = cList.pop()
			if child['kind'] == 't1':
				total += 1
				addComment(child, metaChild['pid'], metaChild['depth'], OP)
				if child['data']['replies'] != "":
					if child['data']['parent_id'] == child['data']['link_id']:
						toParse.append({'pid':child['data']['id'], 'comments':child['data']['replies']['data']['children'], 'depth':(metaChild['depth']+1)})
					else:
						toParse.append({'pid':metaChild['pid'], 'comments':child['data']['replies']['data']['children'], 'depth':(metaChild['depth']+1)})
			elif child['kind'] == 'more':
				commentQ.append({'pid':metaChild['pid'], 'moreObj':child['data'], 'depth':metaChild['depth']})
			else:
				raise Exception('unknown type %s' % child['kind'])

	return commentQ

#add comments to comment list	
def addComment(child, root, depth, oppa):
	data = child['data']
	global celebList, comments
	if data['id'] not in comments:		
		comments[data['id']] = {
			'ID':data['id'], 
			'User':hash(data['author']), 
			'Total':(data['ups']-data['downs']), 
			'Ups':data['ups'], 
			'Downs':data['downs'], 
			'Link':False, 
			'OP':False,
			'Parent':data['parent_id'][3:], 
			'Highest':root, 
			'Depth':depth,
			'Timestamp':data['created_utc'],
			'Celebrity':False,
			'Title':None,
			'Content':None,
			'PostID':data['link_id'][3:]}
		if hash(data['author']) == oppa:
			comments[data['id']]['OP'] = True
		if data['ups'] > 49 or data['downs'] > 49 or hash(data['author']) in celebList:
			comments[data['id']]['Celebrity'] = True
			comments[data['id']]['Content'] = data['body'].encode('ascii','xmlcharrefreplace')
			if hash(data['author']) not in celebList:
				celebList.append(hash(data['author']))
			
#returns (roughly) the number of seconds until 3am
def timeUntil3():
	ctime = datetime.datetime.now()
	h = (26-ctime.hour) % 24
	m = (60-ctime.minute)
	sleepyTime = h * 60 * 60
	sleepyTime += m * 60
	if verbose:
		logger("Time until 3 - %d.", sleepyTime)
	return sleepyTime

def buildCelebList():
	global celebList
	flist = os.listdir('./data/')

	for fname in flist:
		count = 0
		print fname
		f = open('./data/' + fname)
		r = f.read()
		f.close()
		jpage = json.loads(r)

		for entry in jpage:
			if jpage[entry]['Celebrity'] and jpage[entry]['User'] not in celebList:
				#print jpage[entry]
				celebList.append(jpage[entry]['User'])
				count += 1

		print count

#get celeb posts before they were cool
def getCelebs():
	global posts, comments, celebList
	flist = os.listdir('./data')
	pattern = re.compile(r'\d{4}(-\d\d){2}(\.c)?\.json')
	if verbose:
		logger("Getting celebs.")
	for f in flist:
		if pattern.match(f) != None:
			if len(f) == 15:
				loadFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])))
				if verbose:
					logger("Getting celebs from posts.")
				for entry in posts:
					if not posts[entry]['Celebrity'] and posts[entry]['User'] in celebList:
						url = 'http://www.reddit.com/by_id/t3_' + posts[entry]['ID'] + '/.json'
						celebPost = fetchJSON(url)
						while celebPost == -1:
							celebPost = fetchJSON(url)
						celebPost = celebPost['data']['children'][0]['data']
						posts[entry]['Celebrity'] = True
						posts[entry]['Title'] = celebPost['title'].encode('ascii','xmlcharrefreplace')
						posts[entry]['Content'] = celebPost['url'].encode('ascii','xmlcharrefreplace')
						sleep(4)
				writeFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])))
			elif len(f) == 17:
				loadFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])), 'c')
				if verbose:
					logger("Getting celebs from comments.")
				for entry in comments:
					if not comments[entry]['Celebrity'] and comments[entry]['User'] in celebList:
						url = 'http://www.reddit.com/comments/' + comments[entry]['PostID'] + '/robot/' + comments[entry]['ID'] + '/.json'
						celebPost = fetchJSON(url)
						while celebPost == -1:
							celebPost = fetchJSON(url)
							logger('%s', celebPost)
						if celebPost[1]['data']['children'] == []:
							logger('%s', url)
							continue
						celebPost = celebPost[1]['data']['children'][0]['data']
						comments[entry]['Celebrity'] = True
						comments[entry]['Content'] = celebPost['body'].encode('ascii','xmlcharrefreplace')
						sleep(4)
				writeFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])), False)
			else:
				if verbose:
					logger("ERROR: The regex matched an unsupported file.")
					logger(f)

#output all to csv
def toCSV():
	lookup = {}
	fileList = []
	flist = os.listdir('./data')
	pattern = re.compile(r'\d{4}(-\d\d){2}(\.c)?\.json')
	bigList = {}

	if verbose:
		logger("Generating CSV file list.")
	for f in flist:
		if pattern.match(f) != None:
			jfile = open('./data/' + f, 'r')
			bigList.update(json.load(jfile))
			jfile.close()
			bfname = str(f)[:10]
			if bfname not in lookup:
				fileList.append(open('./data/' + bfname + '.csv', 'w'))
				lookup[bfname] = initCSV(fileList[len(fileList)-1])
	if verbose:
		logger("Adding to CSV files.")

	for key in bigList:
		onDay = str(datetime.datetime.fromtimestamp(bigList[key]['Timestamp']))[:10]
		if onDay in lookup:
			writeRowCSV(lookup[onDay], bigList[key])
		else:
			fileList.append(open('./data/' + onDay + '.csv', 'w'))
			lookup[onDay] = initCSV(fileList[len(fileList)-1])
			writeRowCSV(lookup[onDay], bigList[key])
	
	for f in fileList:
		f.close()

def initCSV(opened):
	cfile = csv.writer(opened)
	cfile.writerow(['Number', 
					'Username', 
					'Karma', 
					'Upvotes', 
					'Downvotes', 
					'Post', 
					'PostID',
					'OP', 
					'Parent', 
					'Root', 
					'Depth', 
					'Celebrity', 
					'Title', 
					'Content'])
	return cfile

def writeRowCSV(csvFile, entry):
	LID = None
	if 'PostID' in entry:
		LID = entry['PostID']
	else:
		LID = entry['ID']
	csvFile.writerow([entry['ID'], 
					entry['User'], 
					entry['Total'], 
					entry['Ups'], 
					entry['Downs'], 
					entry['Link'], 
					LID,
					entry['OP'],
					entry['Parent'], 
					entry['Highest'], 
					entry['Depth'], 
					entry['Celebrity'], 
					entry['Title'], 
					entry['Content']])

#parent process main loop
def parent():
	global log, currentDate, posts, target
		
	log = open('log.txt', 'a', 1)
	if(verbose):
		logger("User-Agent: %s", headers['User-Agent'])
		
	now = datetime.datetime.now()
	end = now + datetime.timedelta(7, 30)
	now = datetime.datetime.now()	#fresher

	currentDate = now
	loadFile(currentDate)

	while now < end:
		if now.day != currentDate.day:
			writeFile(currentDate)
			currentDate = now
			posts = {}
			loadFile(currentDate) 
			#if above call is without args then it uses previous day's date... ask stackoverflow about python execution

		page = fetchJSON(target)
	
		while page == -1:
			page = fetchJSON(target)
		
		updatePosts(page)

		if datetime.datetime.now().minute % 2 == 0:
			writeFile(currentDate)
		
		if verbose:
			logger("Number of posts: %d", len(posts))
			#logger('Sleeping 35s.')

		sleep(35)	
		now = datetime.datetime.now()

	writeFile(currentDate)
	if verbose:
		logger("Waiting for child.")
	log.close()
	#pageprint()
	os.wait()

def child():
	dayThresh = datetime.datetime.now()
	dayThresh += datetime.timedelta(5)
	global log, comments, posts
	log = open('childLog.txt', 'a', 1)
	if verbose:
		logger("Log open.")

	while True:
		ctime = datetime.datetime.now()
		targetDate = ctime - datetime.timedelta(3)
		
		flist = os.listdir('./data')
		ftarget = str(targetDate)[:10] + ".json"
		ctarget = str(targetDate)[:10] + ".c.json"
		hasFile = False

		nextTarget = str(targetDate + datetime.timedelta(1))[:10] + ".json"
		hasNext = False
		hasTComments = False
		for f in flist:
			if f == ftarget:
				hasFile = True
			elif f == nextTarget:
				hasNext = True
			elif f == ctarget:
				hasTComments = True
		
		if hasFile and not hasTComments:
			if verbose:
				logger("Day file found. %s", ftarget[:10])
			loadFile(targetDate)
			getComments()
			writeFile(targetDate)
			writeFile(targetDate, False)
			comments = {}
			posts = {}
		
		if datetime.datetime.now() > dayThresh and not hasNext:
			if verbose:
				logger("Next day not found. %s. Breaking out.", nextTarget[:10])
			break

		if str(datetime.datetime.now()-datetime.timedelta(2))[:10] == nextTarget[:10]: 
			stime = timeUntil3()
			sleep(stime)
	#getCelebs()
	#toCSV()
	#TODO CELEBRITY CSV

#main
def main():
	pid = os.fork()
	if pid != 0:
		parent()
	elif pid == 0:
		child()

main()