Tumblr Downloader
=======================

Command line tool to download all images of a Tumblr blog.

Usage
-----

Checkout the code:

    git clone git://github.com/ysaak/tumblr-downloader.git
    cd tumblr-downloader

Run the script, specifying your blog account as the argument:
    
    python tumblrdownloarder.py account

By default, images will be downloaded in a subdirectory with the account name. You can specify the
output directory by adding it as the second optional argument.

If the program is executed multiple times, it will download only the news images. 

License
-------

Source code released under an [MIT license](http://en.wikipedia.org/wiki/MIT_License)
