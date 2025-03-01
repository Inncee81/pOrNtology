import urllib2
import pickle
import videos
import copy
import os
import sys
from bs4 import BeautifulSoup

def GetVideosForPage(soup):
    '''
    Grab all Video-Links from single tag-page, like
    http://video.xnxx.com/tags/acrobat
    '''
    video_urls = []
    for a in soup.findAll("a"): # iterate over all <a></a>-tags in soup. Return link to video if found
        if a.has_key("class"):
            if a["class"] == "miniature":
                video_urls.append(a["href"])
    return video_urls
    
def IterateTagPages(url):
    '''
    Iterate over all video-pages for a single tag. E.g. get "acrobat"-videos
    from page 1 to 8:  
    '''
    url = urllib2.urlopen(url) # again, reading the site
    urlcontent = url.read()
    soup = BeautifulSoup(urlcontent,"xml")
    video_urls = []
    video_urls.extend(GetVideosForPage(soup)) # give soup to function to find all videos on initial page
    next_url = ""
    next = False
    print len(video_urls)
    for i in soup.findAll("a","nP"): # check whether there are more pages to grab. if yes return url of next page and set flag to True
        if i.string == "Next":
            next = True
            next_url = "http://video.xnxx.com" + i["href"]
            break
        else:
            next = False
                       
    while next == True: # if there are more pages in forward direction: grab those as well. 
        print next_url
        url = urllib2.urlopen(next_url)
        urlcontent = url.read()
        soup = BeautifulSoup(urlcontent,"xml")
        video_urls.extend(GetVideosForPage(soup))
        print len(video_urls)
        for i in soup.findAll("a","nP"):
            if i.string == "Next":
                next = True
                next_url = "http://video.xnxx.com" + i["href"]
                break
            else:
                next = False
    return video_urls

def VideosForTag(video_collection,url):
    '''
    Iterate over all videos in array and return a dictionary with
    key = videourl, value = video-object, see videos.py
    '''
    print "getting video-urls for tag"
    video_urls = IterateTagPages(url)
    print "got video-urls"
    print "getting tag-collection for all videos"
    for video in video_urls:
        if video_collection.has_key(video) == False:
            print "saving "+video
            video_tags = videos.GetVideoTags(video)
            video_collection[video_tags.url] = video_tags
        else:
            print "skipped "+video + " as already saved"
    print "got all videos for tag"
    return video_collection

def TagList(url):
    '''
    Set up initial tag-list from URL. 
    Take http://video.xnxx.com/tags/ and iterate over all tags and get list of links to each tag
    '''
    url = urllib2.urlopen(url)
    urlcontent = url.read()
    soup = BeautifulSoup(urlcontent,"xml")
    invalid_tags = ["/tags/","/tags/","/tags/-","/tags/--","/tags/---"]
    tags = {}
    for a in soup.findAll("a"):
        if a.has_key("href"):
            if a["href"].find("/tags/") !=-1 and a["href"] not in invalid_tags:
                tags[str(a["href"])] = False
    return tags

def IterateTags(url):
    '''
    Load or get all tags, iterate over each tag to get videos & tags
    '''
    try:
        video_pickle = open("video_collection.pickle","rb") # if we already ran the script there should be videos to save
        video_collection = pickle.load(video_pickle)
        video_pickle.close()
        print "loaded saved videos"
    except:
        print "created new video-collection"        # if not create new collection
        video_collection = {}
    try:
        tag_pickle = open("tag_collection.pickle","rb") # same is true for tags
        tag_collection = pickle.load(tag_pickle)
        tag_pickle.close()
        print "loaded tag-collection"
    except:
        print "getting new tags"
        tag_collection = TagList(url)
        print "got new tags"
    counter = 0
    for tag,value in tag_collection.iteritems():    # now iterate over each tag
        if value == False:  # if it already was parsed (value == True: great, we skip it)
            print "############################################"
            print "iterate over videos for %s" % (tag)
            video_collection = VideosForTag(video_collection,"http://video.xnxx.com"+tag)
            print "got all videos for %s" % (tag)
            tag_collection[tag] = True
            print tag_collection[tag]
            if counter % 100 == 0 and counter != 0:
                video_pickle = open("video_collection.pickle","wb")
                tag_pickle = open("tag_collection.pickle","wb")
                pickle.dump(tag_collection,tag_pickle)
                print "Saved Tag-Collection"
                pickle.dump(video_collection,video_pickle)
                print "Saved Video Collection"
                tag_pickle.close()
                video_pickle.close()
            counter += 1
            print "Tags since last save: "+str(counter)
            print "Now got "+str(len(video_collection))+" videos"
    print "Now got "+str(len(video_collection))+" videos"
    print "############################################"
    video_pickle = open("video_collection.pickle","wb")
    tag_pickle = open("tag_collection.pickle","wb")
    pickle.dump(tag_collection,tag_pickle)
    print "Saved Tag-Collection"
    pickle.dump(video_collection,video_pickle)
    print "Saved Video Collection"
    tag_pickle.close()
    video_pickle.close()
    print "Finished Crawling Data"