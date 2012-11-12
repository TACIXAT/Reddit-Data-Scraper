Reddit-Data-Scraper
===================

Scrapes posts from /new and collects information about posts and comments.

Programming as the data collection portion for another student's analysis project.

Basic algorithm:
	Parent Process
		Scrapes posts every 35 seconds off /new
		Adds posts to posts dict
		Writes out posts dict to file (json) every two minutes and at the end of the day
		New file at start of each day
		Runs for 7 days (+3 days for comments)

	Child Process
		At three AM check if there is a posts file that is 3 days old (let the comments *cool down*)
		Load file
		Load each post
		Scrape comments
		Write out comments to new json file

	Misc Info
		The program flags people with greater than 50 upvotes and gets the content of their posts for analysis
		The program will output everything to .csv files
		User names are hashed to protect anonymity


