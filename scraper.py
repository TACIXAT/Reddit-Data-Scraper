import json
import urllib2
import os
import datetime

verbose = True
target = "http://www.reddit.com/r/AskReddit/new/.json?limit=100"
targetPost = "http://www.reddit.com/comments/11s7ie/WUT_HERE/c6p4gzh.json"
posts = {}
kindList = {'t1' : 'comment',
			't2' : 'account',
			't3' : 'link',
			't4' : 'message',
			't5' : 'subreddit'}
labels = ["ID", "User", "Total", "Ups", "Downs", "Link", "OP", "Parent", "Highest", "Depth", "Timestamp", "Celebrity", "Title", "Content"]
						

#set User-Agent
headers = {'User-Agent' : 'scrapin\' on my scraper bot\\Ubuntu 12.04 64\\Python\\user robot_one'}
if(verbose):
	print "User-Agent: %s" % headers['User-Agent']
	
#load or create file
def loadFile():
	today = datetime.datetime.now()
	sfname = str(today.year) + '.' + str(today.month) + '.' + str(today.day) + '.json'
	ffname = './data/' + sfname
	hasMatch = False
	flist = os.listdir('./data')
	
	for ea in flist:
		if ea == sfname:
			hasMatch = True
			break
	
	if hasMatch:
		if verbose:
			print 'File match found.\nLoading json.'
			
		f = open(ffname)
		#read json
	else:
		if verbose:
			print 'No match found.\nCreating file.'
		f = open(ffname, 'w')
	
	f.close()
	
#open URL
def fetchJSON(URL):
	req = urllib2.Request(URL, None, headers)
	response = urllib2.urlopen(req)
	
	if verbose:
		print 'Response received.'
	
	jsonpage = json.load(response)
	return jsonpage

#move json into posts
def updatePosts(page):
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
			i = 0
			#update values

#print format			
def pageprint():
	widths = [8, 20, 8, 8, 8, 8, 8, 8, 8, 8, 32, 8, 8, 8]
	skipList = [10, 11, 12, 13]
	for i in range(0,len(labels)):
		if i not in skipList:
			print labels[i].rjust(widths[i]),
		
	print
	
	for ea in posts:
		for i in range(0,len(posts[ea])):
			if i not in skipList:
				print str(posts[ea][labels[i]]).rjust(widths[i]),
		print

#main
def main():
	#load file if exists
	loadFile()
	return 0
	#loop page fetch for 1000
	page = fetchJSON(target)
		#print json.dumps(page, indent=4)
		#return 0
	updatePosts(page)
	
	#output pages fetched to a file
	pageprint()
	
	print len(posts)

		
main()
