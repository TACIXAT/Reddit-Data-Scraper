#TODO
#usernames -> number

import json
import urllib2
import os
import datetime
from time import sleep

#global declares
verbose = True
targetPost = "http://www.reddit.com/r/AskReddit/top/.json"
target = "http://www.reddit.com/r/AskReddit/new/.json?sort=new"
posts = {}
comments = {}
kindList = {'t1' : 'comment',
			't2' : 'account',
			't3' : 'link',
			't4' : 'message',
			't5' : 'subreddit'}
labels = ["ID", "User", "Total", "Ups", "Downs", "Link", "OP", "Parent", "Highest", "Depth", "Timestamp", "Celebrity", "Title", "Content"]
log = open('out.txt', 'a', 1)					

#set User-Agent
headers = {'User-Agent' : 'scrapin\' on my scraper bot\\Ubuntu 12.04 64\\Python\\user robot_one'}
if(verbose):
	print "User-Agent: %s" % headers['User-Agent']
	log.write("User-Agent: %s\n" % headers['User-Agent'])
	
#load or create file
def loadFile():
	today = datetime.datetime.now()
	sfname = str(today.year) + '.' + str(today.month) + '.' + str(today.day) + '.json'
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
	print json.dumps(page, indent=4)
	for child in page['data']['children']:
		data = child['data']
		if data['id'] not in posts:		
			posts[data['id']] = {
				'ID':data['id'], 
				'User':data['author'], 
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
		else:
			posts[data['id']]['Total'] = data['score'] 
			posts[data['id']]['Ups'] = data['ups']
			posts[data['id']]['Downs'] = data['downs'] 
	
#dump json	
def writeFile():
	if verbose:
		print 'Writing to file.'
		log.write('Writing to file.\n')
	today = datetime.datetime.now()
	sfname = str(today.year) + '.' + str(today.month) + '.' + str(today.day) + '.json'
	ffname = './data/' + sfname
	f = open(ffname, 'w')
	
	f.write(json.dumps(posts, indent=4))
	
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

#fetch all the comments
def getComments():
	commentQ = []
	for entry in posts:
		if entry['Link'] is True:
			postURL = "http://www.reddit.com/comments/" + entry['ID'] + ".json?sort=top&limit=500"
			postJSON = fetchJSON(postURL)
			loadedComments = postJSON[1]['data']['children']
			loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
			loadedAuthor = [0]['data']['children'][0]['data']['author']
			commentQ = parsePost(loadedComments, loadedLinkID, loadedAuthor, initialDepth)
			
			#for each in commentQueue, load pages, parsePosts ...
			while len(commentQ) > 0:
				metaList = commentQ.pop()
				clist = metaList['comments']
				for link in cList:
					postURL = "http://www.reddit.com/comments/" + link + ".json?sort=top&limit=500"
					postJSON = fetchJSON(postURL)
					loadedComments = postJSON[1]['data']['children']
					loadedLinkID = postJSON[0]['data']['children'][0]['data']['id']
					loadedAuthor = [0]['data']['children'][0]['data']['author']
					initialDepth = metaList['depth']
					commentQ.append(parsePost(loadedComments, loadedLinkID, loadedAuthor, initialDepth))
				
				print len(commentQ)
				
#parse comments, append 'more' sections to queue					
def parsePost(postComments, parentID, OP, initialDepth=0):
	toParse = []
	commentQ = []
	toParse.append({'pid':parentID, 'comments':postComments, 'depth':initialDepth})

	while len(toParse) > 0:
		metaChild = toParse.pop()
		cList = metaChild['comments']
		while len(cList) > 0:
			child = cList.pop()
			if child['kind'] == 't1':
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
				'User':data['author'], 
				'Total':data['score'], 
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
			if data['author'] == oppa:
				comments[data['id']]['OP'] = True
			
#main
def main():
	loadFile()
	
	while datetime.datetime.now().day == 21 and datetime.datetime.now().hour <= 13:
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

	writeFile()
	log.close()
	pageprint()
	print len(posts)
	
#main()
