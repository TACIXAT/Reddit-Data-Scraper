import json
import urllib2

verbose = True
target = "http://www.reddit.com/r/AskReddit/new/.json"
posts = {}
kindList = {'t1' : 'comment',
			't2' : 'account',
			't3' : 'link',
			't4' : 'message',
			't5' : 'subreddit'}
						

#set User-Agent
headers = {'User-Agent' : 'scrapin\' on my scraper bot\\Ubuntu 12.04 64\\Python\\/u/robot_one'}
if(verbose):
	print "User-Agent: %s" % headers['User-Agent']

#open URL
def fetchJSON(URL):
	req = urllib2.Request(URL, None, headers)
	response = urllib2.urlopen(req)
	
	if(verbose):
		print 'Response received.'
	
	jsonpage = json.load(response)
	return jsonpage

def updatePosts(page):
	for child in page['data']['children']:
		data = child['data']
		if(data['id'] not in posts):		
			posts[data['id']] = [data['id'], 
						data['author'], 
						data['score'], 
						data['ups'], 
						data['downs'], 
						True, 
						True, 
						None, 
						None, 
						None]
		else:
			i = 0
			#update values
			
def pf():
	widths = [8, 20, 8, 8, 8, 8, 8, 8, 8, 8]
	labels = ["ID", "User", "Total", "Ups", "Downs", "Link", "OP", "Parent", "Highest", "Depth"]
	
	for i in range(0,len(labels)):
		print labels[i].rjust(widths[i]),
		
	print
	
	for ea in posts:
		for i in range(0,len(posts[ea])):
			print str(posts[ea][i]).rjust(widths[i]),
		print

#main
def main():
	page = fetchJSON(target)
	#print json.dumps(page, indent=4)
	updatePosts(page)
	pf()

		
main()
