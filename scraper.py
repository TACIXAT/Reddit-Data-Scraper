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
import json
import csv

#global declares
verbose = True
targetSubreddit = 'AskReddit'
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
headers = {'User-Agent' : 'scraper bot goes far\\Ubuntu 12.04 64\\Python\\user robot_one'}
	
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
			logger('File match found.\nLoading json.')
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
			logger('No match found.\nCreating file.')
		f = open(ffname, 'w')
	
	f.close()
	
#open URL
def fetchJSON(URL):
	req = urllib2.Request(URL, None, headers)
	
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		logger(str(e.code))
		sleep(10)
		return -1
	except urllib2.URLError, e:
		logger(str(e.args))
		sleep(10)
		return -1
	
	if verbose:
		logger('Response received.')
	
	jsonpage = json.load(response)
	return jsonpage

#move json into dict posts
def updatePosts(page):
	global celebList
	if verbose:
		logger('Adding json page listings to posts object.')
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
				posts[data['id']]['Title'] = data['title']
				posts[data['id']]['Content'] = data['selftext']
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
	for entry in posts:
		total = 0
		if posts[entry]['Link'] == True:
			postURL = "http://www.reddit.com/comments/" + posts[entry]['ID'] + ".json?sort=top&limit=500"
			if verbose:
				logger('Loading comments for %s.', posts[entry]['ID'])
			postJSON = fetchJSON(postURL)
			while postJSON == -1:
				fetchJSON(postURL)
			updatePosts(postJSON[0])
			loadedComments = postJSON[1]['data']['children']
			loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
			loadedAuthor = hash(postJSON[0]['data']['children'][0]['data']['author'])
			commentQ = parsePost(loadedComments, loadedLinkID, loadedAuthor)
			
			if verbose:
				logger('%d comments collected.', total)
				if len(commentQ) > 0:
					logger('Loading more comments for %s.', posts[entry]['ID'])
			#for each in commentQueue, load pages, parsePosts ...
			sleep(2)
			while len(commentQ) > 0:
				metaList = commentQ.pop()
				cList = metaList['comments']
				if verbose:
					logger('Starting load of %d pages.', len(cList))
				for link in cList:
					postURL = "http://www.reddit.com/comments/" + posts[entry]['ID'] + "/robot/" + link + ".json?sort=top&limit=500"
					postJSON = fetchJSON(postURL)
					while postJSON == -1:
						fetchJSON(postURL)
					loadedComments = postJSON[1]['data']['children']
					loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
					loadedAuthor = hash(postJSON[0]['data']['children'][0]['data']['author'])
					initialDepth = metaList['depth']
					commentQ += parsePost(loadedComments, loadedLinkID, loadedAuthor, initialDepth)
					if verbose:
						logger('Sleeping 2s.')
					sleep(2)
				if verbose:	
					logger("%d meta comment lists remaining.", len(commentQ))	
		if verbose:	
			logger("%d total comments for post %s.", (total, posts[entry]['ID']))				
								

#parse comments, append 'more' sections to queue					
def parsePost(postComments, parentID, OP, initialDepth=0):
	global total
	toParse = []
	commentQ = []
	toParse.append({'pid':parentID, 'comments':postComments, 'depth':initialDepth})
	if verbose:
		logger("Parsing post.")

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
				commentQ.append({'pid':metaChild['pid'], 'comments':child['data']['children'], 'depth':metaChild['depth']})
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
			'Content':None}
		if hash(data['author']) == oppa:
			comments[data['id']]['OP'] = True
		if data['ups'] > 49 or data['downs'] > 49 or hash(data['author']) in celebList:
			comments[data['id']]['Celebrity'] = True
			comments[data['id']]['Content'] = data['body']
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
						celebPost = fetchJSON()
						celebPost = celebPost['data']['children'][0]['data']
						posts[entry]['Celebrity'] = True
						posts[entry]['Title'] = celebPost['title']
						posts[entry]['Content'] = celebPost['selftext']
						sleep(2)
				writeFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])))
			elif len(f) == 17:
				loadFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])), 'c')
				if verbose:
					logger("Getting celebs from comments.")
				for entry in comments:
					if not comments[entry]['Celebrity'] and comments[entry]['User'] in celebList:
						url = 'http://www.reddit.com/comments/' + comments[entry]['Parent'] + '/robot/' + comments[entry]['ID'] + '/.json'
						celebPost = fetchJSON()
						celebPost = celebPost[1]['data']['children'][0]['data']
						comments[entry]['Celebrity'] = True
						comments[entry]['Content'] = celebPost['selftext']
						sleep(2)
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
					'OP', 
					'Parent', 
					'Root', 
					'Depth', 
					'Celebrity', 
					'Title', 
					'Content'])
	return cfile

def writeRowCSV(csvFile, entry):
	csvFile.writerow([entry['ID'], 
					entry['User'], 
					entry['Total'], 
					entry['Ups'], 
					entry['Downs'], 
					entry['Link'], 
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
	loadFile()

	while now < end:
		if now.day != currentDate.day:
			writeFile(currentDate)
			currentDate = now
			posts = {}
			loadFile()

		page = fetchJSON(target)
	
		while page == -1:
			page = fetchJSON(target)
		
		updatePosts(page)

		if datetime.datetime.now().minute % 2 == 0:
			writeFile(currentDate)
		
		if verbose:
			logger("Number of posts: %d", len(posts))
			logger('Sleeping 35s.')

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

	if verbose:
		logger("Sleeping until 3.")

	stime = timeUntil3()
	sleep(stime)

	while True:
		ctime = datetime.datetime.now()
		targetDate = ctime - datetime.timedelta(3)
		
		flist = os.listdir('./data')
		ftarget = str(targetDate)[:10] + ".json"
		hasFile = False

		nextTarget = str(targetDate + datetime.timedelta(1))[:10] + ".json"
		hasNext = False
		
		for f in flist:
			if f == ftarget:
				hasFile = True
			elif f == nextTarget:
				hasNext = True
		
		if hasFile:
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

		stime = timeUntil3()
		sleep(stime)
	getCelebs()
	toCSV()
	#TODO CELEBRITY CSV

#main
def main():
	pid = os.fork()
	if pid != 0:
		parent()
	elif pid == 0:
		child()

main()