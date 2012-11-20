Reddit-Data-Scraper
===================

Scrapes posts from /new and collects information about posts and comments. Best effort for getting all posts and comments in a week.

Programming as the data collection portion for another student's analysis project.

Running on Amazon EC2. Ubuntu - Micro instance. Free Tier FTW!

Basic algorithm:

	Parent Process
		Scrapes posts every 35 seconds off /new
		Adds posts to posts dict
		Writes out posts dict to file (json) every two minutes and at the end of the day
		New file at start of each day
		Runs for 10 days (7 days for posts + 3 for comments)

	Child Process
		At three AM check if there is a posts file that is 3 days old (let the thread *settle down*)
		Load file
		Load each post
		Scrape comments
		Write out comment data to new json file

	Misc Info
		The program flags people with greater than 50 upvotes or downvotes and gets the content of their posts for analysis
			It goes back and gets their posts that were added before they were flagged
		The program outputs everything to .csv files
		User names are hashed to protect anonymity

tl;dr Attempts to get all posts and comments from a target subreddit made in 1 week.