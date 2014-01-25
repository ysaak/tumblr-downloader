#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tumblr photo downloader """

import sys, os, errno
import urllib2
import threading
import Queue
import time
import signal
import argparse
from xml.dom import minidom

__version__ = 0.1

URL_FORMAT = 'http://%s.tumblr.com/api/read?type=photo&num=%d&start=%d'

def imagesdownloader(urls):
    """ Thread function used to download an image """
    while 1:
        try:
            url, localfile = urls.get(True, 2)

            try:
                ufd = urllib2.urlopen(url)
                # Open our local file for writing
                with open(localfile, "wb") as lfd:
                    lfd.write(ufd.read())

            except: #handle errors
                print "\nError getting file,", sys.exc_info()[1]

            urls.task_done()
        except:
            break   # No more jobs

def _getnewimageslist(account, directory):
    """ Search for new images to download """
    print "Searching for new images from account %s to download ..." % (account,)

    num = 50
    start = 0
    newimages = []

    while True:
        images_counter = []

        feed = urllib2.urlopen(URL_FORMAT % (account, num, start)).read()
        dom = minidom.parseString(feed)

        photoslist = dom.getElementsByTagName('photo-url')

        for photo in photoslist:
            if int(photo.attributes['max-width'].value) == 1280:

                url = photo.firstChild.nodeValue
                localfile = os.path.join(directory, url.split('/')[-1].split('#')[0].split('?')[0])

                if not os.path.exists(localfile):
                    newimages.append((url, localfile))

                    sys.stdout.write('\r%d new images ...' % (len(newimages),))
                    sys.stdout.flush()

                images_counter.append(url)

        if len(newimages) == 0:
            print "Nothing new to download. Done."
            break

        if len(images_counter) < num:
            break
        else:
            start += num

    return newimages

def updateprogress(qsize, nbimages):
    """ Download progress bar """
    progress = 100 - int((100.0 * qsize) / nbimages)
    dsp = '\r%03d%% [%-50s] (%d, %d)' % (progress, '#'*(progress/2), nbimages - qsize, nbimages)

    sys.stdout.write(dsp)
    sys.stdout.flush()

def main():
    """ Main function """
    parser = argparse.ArgumentParser(description="Download all the photos of a Tumblr blog")
    parser.add_argument("account", help="account to download")
    parser.add_argument("directory", help="output directory", nargs='?')
    parser.add_argument("-c", "--concurrency", type=int, default=8, help="set the number of download threads (default: 8)")

    args = parser.parse_args()

    account = args.account
    directory = args.directory if args.directory is not None else account

    try:
        os.makedirs(directory)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else: raise

    jobs = Queue.LifoQueue()
    newimages = _getnewimageslist(account, directory)
    nbimages = len(newimages)

    if nbimages == 0:
        return

    for image in newimages:
        jobs.put(image)

    print "\nStarting download threads"

    # Start workers
    for windex in xrange(args.concurrency):
        worker = threading.Thread(target=imagesdownloader, args=(jobs,))
        worker.setDaemon(True)
        worker.start()

    # Display progress bar
    while not jobs.empty():
        qsize = jobs.qsize()
        updateprogress(qsize, nbimages)
        time.sleep(0.3)

    updateprogress(0, nbimages)
    print

    for thread in threading.enumerate():
        if thread is not threading.currentThread():
            thread.join()

    print "Done."

def _sigint_handler(sig, frame):
    """ Manage SIGINT signal """
    print "\nStopped by user"
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, _sigint_handler)
    main()
