import json
import urllib

verbose = True

#Set User-Agent
class AppURLopener(urllib.FancyURLopener):
	version = "comment/post data bot - /u/robot_one"
	if(verbose):
		print "User-Agent: %s" % version
		    
urllib._urlopener = AppURLopener()

#Open Sub-Reddit
target = "http://www.reddit.com/r/AskReddit/new/"

print urllib.FancyURLopener.open(target)




