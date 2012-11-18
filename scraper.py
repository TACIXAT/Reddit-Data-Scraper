#TODO
#celeb csv
#write test

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

#set User-Agent
headers = {'User-Agent' : 'scrapin\' on my scraper bot\\Ubuntu 12.04 64\\Python\\user robot_one'}
	
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
			#print 'File match found.\nLoading json.'
			log.write('File match found.\nLoading json.\n')
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
			#print 'No match found.\nCreating file.'
			log.write('No match found.\nCreating file.\n')
		f = open(ffname, 'w')
	
	f.close()
	
#open URL
def fetchJSON(URL):
	req = urllib2.Request(URL, None, headers)
	
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		#print e.code
		log.write(str(e.code))
		log.write('\n')
		sleep(10)
		return -1
	except urllib2.URLError, e:
		#print e.args
		log.write(str(e.args))
		log.write('\n')
		sleep(10)
		return -1
	
	if verbose:
		#print 'Response received.'
		log.write('Response received.\n')
	
	jsonpage = json.load(response)
	return jsonpage

#move json into dict posts
def updatePosts(page):
	global celebList
	if verbose:
		#print 'Adding json page listings to posts object.'
		log.write('Adding json page listings to posts object.\n')
	#print json.dumps(page, indent=4)
	UTCFilter = datetime.datetime(currentDate.year, currentDate.month, currentDate.day).strftime('%s')
	for child in page['data']['children']:
		data = child['data']
		if data['id'] not in posts and int(data['created_utc']) >= int(UTCFilter):
			#print "in if UTC"		
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
		#print 'Writing to file ' + sfname 
		log.write('Writing to file ' + sfname + '\n')
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
				#print 'Loading comments for %s.' % posts[entry]['ID']
				log.write('Loading comments for %s.\n' % posts[entry]['ID'])
			postJSON = fetchJSON(postURL)
			while postJSON == -1:
				fetchJSON(postURL)
			updatePosts(postJSON[0])
			loadedComments = postJSON[1]['data']['children']
			loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
			loadedAuthor = hash(postJSON[0]['data']['children'][0]['data']['author'])
			commentQ = parsePost(loadedComments, loadedLinkID, loadedAuthor)
			
			if verbose:
				#print '%d comments collected.' % total
				log.write('%d comments collected.\n' % total)
				if len(commentQ) > 0:
					#print 'Loading more comments for %s.' % posts[entry]['ID']
					log.write('Loading more comments for %s.\n' % posts[entry]['ID'])
			#for each in commentQueue, load pages, parsePosts ...
			sleep(2)
			while len(commentQ) > 0:
				metaList = commentQ.pop()
				#print json.dumps(metaList, indent=4)
				cList = metaList['comments']
				if verbose:
					#print 'Starting load of %d pages.' % len(cList)
					log.write('Starting load of %d pages.\n' % len(cList))
					#print cList
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
						ptime = datetime.datetime.now()
						#print 'Sleeping 2s at %d:%02d.' % (ptime.hour, ptime.minute)
						log.write('Sleeping 2s at %d:%02d.\n' % (ptime.hour, ptime.minute))
					sleep(2)
				if verbose:	
					#print "%d meta comment lists remaining." % len(commentQ)
					log.write("%d meta comment lists remaining.\n" % len(commentQ))	
		if verbose:	
			#print "%d total comments for post %s." % (total, posts[entry]['ID'])
			log.write("%d total comments for post %s.\n" % (total, posts[entry]['ID']))				
								

#parse comments, append 'more' sections to queue					
def parsePost(postComments, parentID, OP, initialDepth=0):
	global total
	toParse = []
	commentQ = []
	toParse.append({'pid':parentID, 'comments':postComments, 'depth':initialDepth})
	if verbose:
		#print "Parsing post."		
		log.write("Parsing post.\n")

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
	if verbose:
		#print "Adding comment."		
		log.write("Adding comment.\n")
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
		#print "Time until 3 - %d." % sleepyTime		
		log.write("Time until 3 - %d.\n" % sleepyTime)
	return sleepyTime

#get celeb posts before they were cool
def getCelebs():
	global posts, comments, celebList
	flist = os.listdir('./data')
	pattern = re.compile(r'\d{4}(-\d\d){2}(\.c)?\.json')
	if verbose:
		#print "Getting celebs."		
		log.write("Getting celebs.\n")
	for f in flist:
		if pattern.match(f) != None:
			if len(f) == 15:
				loadFile(datetime.datetime(int(f[:4]), int(f[5:7]), int(f[8:10])))
				if verbose:
					#print "Getting celebs from posts."		
					log.write("Getting celebs from posts.\n")
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
					#print "Getting celebs from comments."		
					log.write("Getting celebs from comments.\n")
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
					#print "ERROR: The regex matched an unsupported file."		
					log.write("ERROR: The regex matched an unsupported file.\n")
					#print f

#output all to csv
def toCSV():
	lookup = {}
	fileList = []
	flist = os.listdir('./data')
	pattern = re.compile(r'\d{4}(-\d\d){2}(\.c)?\.json')
	bigList = {}

	if verbose:
		#print "Generating CSV file list."		
		log.write("Generating CSV file list.\n")
	for f in flist:
		if pattern.match(f) != None:
			jfile = open('./data/' + f, 'r')
			bigList.update(json.load(jfile))
			jfile.close()
			bfname = str(f)[:10]
			if bfname not in lookup:
				fileList.append(open('./data/' + bfname + '.csv', 'w'))
				cfile = csv.writer(fileList[len(fileList)-1])
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
				lookup[bfname] = cfile

	if verbose:
		#print "Adding to CSV files."		
		log.write("Adding to CSV files.\n")

	for key in bigList:
		onDay = str(datetime.datetime.fromtimestamp(bigList[key]['Timestamp']))[:10]
		if onDay in lookup:
			lookup[onDay].writerow([bigList[key]['ID'], 
			                       bigList[key]['User'], 
			                       bigList[key]['Total'], 
			                       bigList[key]['Ups'], 
			                       bigList[key]['Downs'], 
			                       bigList[key]['Link'], 
			                       bigList[key]['OP'],
			                       bigList[key]['Parent'], 
			                       bigList[key]['Highest'], 
			                       bigList[key]['Depth'], 
			                       bigList[key]['Celebrity'], 
			                       bigList[key]['Title'], 
			                       bigList[key]['Content']])
		else:
			fileList.append(open('./data/' + onDay + '.csv', 'w'))
			cfile = csv.writer(fileList[len(fileList)-1])
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
			lookup[onDay] = cfile
			lookup[onDay].writerow([bigList[key]['ID'], 
			                       bigList[key]['User'], 
			                       bigList[key]['Total'], 
			                       bigList[key]['Ups'], 
			                       bigList[key]['Downs'], 
			                       bigList[key]['Link'], 
			                       bigList[key]['OP'],
			                       bigList[key]['Parent'], 
			                       bigList[key]['Highest'], 
			                       bigList[key]['Depth'], 
			                       bigList[key]['Celebrity'], 
			                       bigList[key]['Title'], 
			                       bigList[key]['Content']])
	
	
	#make sure that randomly dated comment / post can be given a file
	for f in fileList:
		f.close()

#parent process main loop
def parent():
	global log, currentDate, posts, target
		
	log = open('log.txt', 'a', 1)
	if(verbose):
		#print "User-Agent: %s" % headers['User-Agent']
		log.write("User-Agent: %s\n" % headers['User-Agent'])
		
	now = datetime.datetime.now()
	end = now + datetime.timedelta(1, 30)
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
			#print len(posts)		
			log.write("%d\n" % len(posts))
			#print 'Sleeping 35s at %d:%02d.' % (datetime.datetime.now().hour, datetime.datetime.now().minute)
			log.write('Sleeping 35s at %d:%02d.\n' % (datetime.datetime.now().hour, datetime.datetime.now().minute))

		sleep(35)	
		now = datetime.datetime.now()

	writeFile(currentDate)
	if verbose:
		#print "Waiting for child."		
		log.write("Waiting for child.\n")
	log.close()
	#pageprint()
	#print len(posts)
	os.wait()

def child():
	dayThresh = datetime.datetime.now()
	dayThresh += datetime.timedelta(7)
	global log, comments, posts
	log = open('childLog.txt', 'a', 1)
	if verbose:
		#print "Log open."		
		log.write("Log open.\n")

	if verbose:
		#print "Sleeping until 3."		
		log.write("Sleeping until 3.\n")

	#stime = timeUntil3()
	#sleep(stime)
	sleep(32400)

	while True:
		ctime = datetime.datetime.now()
		targetDate = ctime - datetime.timedelta(1)
		
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
				#print "Day file found. %s" % ftarget[:10]		
				log.write("Day file found. %s\n" % ftarget[:10])
			loadFile(targetDate)
			getComments()
			writeFile(targetDate)
			writeFile(targetDate, False)
			comments = {}
			posts = {}
		
		if datetime.datetime.now() > dayThresh and not hasNext:
			if verbose:
				#print "Next day not found. %s. Breaking out." % nextTarget[:10]		
				log.write("Next day not found. %s. Breaking out.\n" % nextTarget[:10])
			break

		#stime = timeUntil3()
		#sleep(stime)
		sleep(59400)
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