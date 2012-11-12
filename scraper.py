#TODO
#usernames -> number
#scheduler / wrapper
#get all for celebs

import json
import urllib2
import os
import datetime
from time import sleep

#global declares
verbose = True
target = "http://www.reddit.com/r/AskReddit/new/.json?sort=new"
posts = {}
comments = {}
kindList = {'t1' : 'comment',
			't2' : 'account',
			't3' : 'link',
			't4' : 'message',
			't5' : 'subreddit'}
monthDays =  [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
labels = ["ID", "User", "Total", "Ups", "Downs", "Link", "OP", "Parent", "Highest", "Depth", "Timestamp", "Celebrity", "Title", "Content"]
currentDay = datetime.datetime.now().day

#TODO remove this place holder function
def doSomething():
	return 0

#set User-Agent
headers = {'User-Agent' : 'scrapin\' on my scraper bot\\Ubuntu 12.04 64\\Python\\user robot_one'}
if(verbose):
	print "User-Agent: %s" % headers['User-Agent']
	log.write("User-Agent: %s\n" % headers['User-Agent'])
	
#load or create file
def loadFile(targetDate=datetime.datetime.now()):
	sfname = str(targetDate.year) + '.' + str(targetDate.month) + '.' + str(targetDate.day) + '.json'
	ffname = './data/' + sfname
	hasMatch = False
	flist = os.listdir('./data')
	
	for item in flist:
		if item == sfname:
			hasMatch = True
			break
	
	if hasMatch:
		if verbose:
			print 'File match found.\nLoading json.'
			log.write('File match found.\nLoading json.\n')
		f = open(ffname)
		loaded = json.load(f)

		global posts 
		posts = loaded
	else:
		if verbose:
			print 'No match found.\nCreating file.'
			log.write('No match found.\nCreating file.\n')
		f = open(ffname, 'w')
	
	f.close()
	
#open URL
def fetchJSON(URL):
	req = urllib2.Request(URL, None, headers)
	
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print e.code
		log.write(str(e.code))
		log.write('\n')
		sleep(10)
		return -1
	except urllib2.URLError, e:
		print e.args
		log.write(str(e.args))
		log.write('\n')
		sleep(10)
		return -1
	
	if verbose:
		print 'Response received.'
		log.write('Response received.\n')
	
	jsonpage = json.load(response)
	return jsonpage

#move json into dict posts
def updatePosts(page):
	if verbose:
		print 'Adding json page listings to posts object.'
		log.write('Adding json page listings to posts object.\n')
	#print json.dumps(page, indent=4)
	UTCFilter = datetime.datetime(currentYear, currentMonth, currentDay)
	UTCFilter = utc.strftime('%s')

	for child in page['data']['children']:
		data = child['data']
		if data['id'] not in posts and data['created_utc'] >= UTCFilter:		
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
def writeFile(date=datetime.datetime.now(), output=posts):
	sfname = str(date.year) + '.' + str(date.month) + '.' + str(date.day) + '.json'
	ffname = './data/' + sfname
	if verbose:
		print 'Writing to file ' + sfname 
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
				print 'Loading comments for %s.' % posts[entry]['ID']
				log.write('Loading comments for %s.' % posts[entry]['ID'])
			postJSON = fetchJSON(postURL)
			while postJSON == -1:
				fetchJSON(postURL)
			updatePosts(postJSON[0])
			loadedComments = postJSON[1]['data']['children']
			loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
			loadedAuthor = hash(postJSON[0]['data']['children'][0]['data']['author'])
			commentQ = parsePost(loadedComments, loadedLinkID, loadedAuthor)
			
			if verbose:
				print '%d comments collected.' % total
				log.write('%d comments collected.' % total)
				if len(commentQ) > 0:
					print 'Loading more comments for %s.' % posts[entry]['ID']
					log.write('Loading more comments for %s.' % posts[entry]['ID'])
			#for each in commentQueue, load pages, parsePosts ...
			while len(commentQ) > 0:
				metaList = commentQ.pop()
				#print json.dumps(metaList, indent=4)
				cList = metaList['comments']
				if verbose:
					print 'Starting load of %d pages.' % len(cList)
					log.write('Starting load of %d pages.' % len(cList))
				for link in cList:
					start = datetime.datetime.now()
					postURL = "http://www.reddit.com/comments/" + posts[entry]['ID'] + "/robot/" + link + ".json?sort=top&limit=500"
					postJSON = fetchJSON(postURL)
					while postJSON == -1:
						fetchJSON(postURL)
					loadedComments = postJSON[1]['data']['children']
					loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
					loadedAuthor = hash(postJSON[0]['data']['children'][0]['data']['author'])
					initialDepth = metaList['depth']
					commentQ += parsePost(loadedComments, loadedLinkID, loadedAuthor, initialDepth)
					finish = datetime.datetime.now()
					delta = finish-start
					if(delta.seconds < 2):
						if verbose:
							ptime = datetime.datetime.now()
							print 'Sleeping %ds at %d:%02d.' % ((2-delta.seconds), ptime.hour, ptime.minute)
							log.write('Sleeping %ds at %d:%02d.\n' % ((2-delta.seconds), ptime.hour, ptime.minute))
						sleep(2-delta.seconds)
				if verbose:	
					print "%d meta comment lists remaining." % len(commentQ)
					log.write("%d meta comment lists remaining." % len(commentQ))	
		if verbose:	
			print "%d total comments for post %s." % (total, posts[entry]['ID'])
			log.write("%d total comments for post %s." % (total, posts[entry]['ID']))				
								

#parse comments, append 'more' sections to queue					
def parsePost(postComments, parentID, OP, initialDepth=0):
	global total
	toParse = []
	commentQ = []
	toParse.append({'pid':parentID, 'comments':postComments, 'depth':initialDepth})

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
	if data['id'] not in comments:		
		comments[data['id']] = {
			'ID':data['id'], 
			'User':hash(data['author']), 
			'Total':(data['ups']-data['downs']), 
			'Ups':data['ups'], 
			'Downs':data['downs'], 
			'Link':False, 
			'Parent':data['parent_id'][3:], 
			'Highest':root, 
			'Depth':depth,
			'Timestamp':data['created_utc'],
			'Celebrity':False,
			'Title':None,
			'Content':None}
		if hash(data['author']) == oppa:
			comments[data['id']]['OP'] = True
		if data['ups'] > 49 or hash(data['author']) in celebList:
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
	return sleepyTime
		
#main
def main():
	pid = os.fork()
	
	if pid != 0:
		global log
		log = open('log.txt', 'a', 1)
		#TODO 
		#fix to stop at midnight
		#write out
		#open new file
		#check times when adding to 'new posts'
		now = datetime.datetime.now()
		end = now + datetime.timedelta(7, 30)
		now = datetime.datetime.now()	#fresher

		global currentDay
		global currentMonth
		global currentYear
		currentDay = now.day
		currentYear = now.year
		currentMonth = now.month

		loadFile()

		while now < end:
			if now.day != currentDay:
				currentDay = now.day
				currentYear = now.year
				currentMonth = now.month
				writeFile()
				global posts
				posts = {}
				loadFile()

			page = fetchJSON(target)
		
			while page == -1:
				page = fetchJSON(target)
			
			updatePosts(page)

			if datetime.datetime.now().minute % 2 == 0:
				writeFile()
			
			if verbose:
				print len(posts)		
				log.write("%d\n" % len(posts))
				print 'Sleeping 35s at %d:%02d.' % (datetime.datetime.now().hour, datetime.datetime.now().minute)
				log.write('Sleeping 35s at %d:%02d.\n' % (datetime.datetime.now().hour, datetime.datetime.now().minute))

			sleep(35)	
			now = datetime.datetime.now()

		writeFile()
		log.close()
		#pageprint()
		print len(posts)
	elif pid == 0:
		global log
		log = open('childLog.txt', 'a', 1)
		stime = timeUntil3()
		sleep(stime)

		while True:
			ctime = datetime.datetime.now()
			
			targetDay = ctime.day - 3
			targetMonth = ctime.month
			targetYear = ctime.year
			
			if targetDay < 1:
				if targetMonth == 1:
					targetYear -= 1
					targetMonth = 12
					targetDay += monthDays[targetMonth]
				else:
					targetMonth -= 1
					targetDay += monthDays[targetMonth]
				
			ftarget = str(targetYear) + "." + str(targetMonth) + "." + str(targetDay) + ".json"
			flist = os.listdir('./data')
			hasFile = False
			
			for f in flist:
				if f == ftarget:
					hasFile = True
					
			if hasFile:
				targetDate = datetime.datetime(targetYear, targetMonth, targetDay)
				loadFile(targetDate)
				getComments()
				writeFile(targetDate)
				writeFile(targetDate, comments)
				global comments
				global posts
				comments = {}
				posts = {}
			
			stime = timeUntil3()
			sleep(stime)
		#TODO get all celeb posts
		#TODO output all to .csv
		
main()
