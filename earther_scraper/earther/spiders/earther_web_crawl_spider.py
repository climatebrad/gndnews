"""
Use this script to crawl all of Earther's articles

"""
import scrapy
import requests
import math

from earther.items import EartherItem #, EartherComment
from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.exceptions import CloseSpider

global NUM_ARTICLES
NUM_ARTICLES = 10000

class EartherSpider(scrapy.Spider):

    name = "earther"
    allowed_domains = [
        "earther.com", 
        "gizmodo.com", 
        "lifehacker.com", 
        "jalopnik.com", 
        "jezebel.com",
        "theroot.com",
        "thetakeout.com",
        "deadspin.com",
        "kotaku.com",
        "theonion.com",
    ]
    start_urls = [
        "http://earther.gizmodo.com",
    ]

    # def process_value(x):
    #     print('LOOK AT THIS: ', 'http://gizmodo.com/' + x)
    #     return 'http://gizmodo.com/' + x

    # extractor = LxmlLinkExtractor(allow=(), 
    #                             restrict_css=('.load-more div.text-center a::attr(href)',),
    #                             process_value=(process_value))

    # rules = (
    #     Rule(
    #         extractor, 
    #         callback="parse_headlines", follow= True
    #         ),
    # )

    def parse(self, response):
        links = set(response.css('a[data-ga*="stream post"]::attr(href)').extract())
        for url in links:
            yield scrapy.Request(url, callback=self.parse_article)
        link = response.css('a[data-ga*="More stories"]::attr(href)').get()
        if link is not None:
            yield response.follow(link, callback=self.parse)

    @staticmethod
    def shortnum_to_numeric(num_str):
        """Convert e.g. 2.9K to 2900, 10M to 10000000, None to 0"""
        if not num_str:
            return 0
        suffices = {'K' : 1000, 'M' : 1000000 }
        if num_str[-1] in ('K','M'):
            (num, suffix) = (num_str[:-1], num_str[-1])
            return int(float(num) * suffices[suffix])
        return int(num_str)
    
    def parse_article(self, response):
        global NUM_ARTICLES
        if self.crawler.stats.get_value('item_scraped_count') and (self.crawler.stats.get_value('item_scraped_count') >= NUM_ARTICLES):
            raise CloseSpider('Done Crawling')

        item = EartherItem()
       
        
        item['url'] = response.url
       
        # content in head
        
        item['title'] = response.css('title::text').get()
        item['twitter_url'] = response.css('meta[name="twitter:url"]').attrib['content']
        item['image']  = response.css('meta[property="og:image"]').attrib['content']

        k = response.css('meta[name="keywords"]').attrib['content']
        keywords = list(set(map(str.strip, k.split(','))))
        item['keywords'] = keywords
        
        item['description'] = response.css('meta[name="description"]').attrib['content']
        
        # content in body
        item['num_like']  = self.shortnum_to_numeric(response.css('div[title] span::text').get())
        item['num_reply'] = self.shortnum_to_numeric(response.css('a[data-ga*="Comment count"] span::text').get())

        if response.css('main').get():
            body_text = response.css('main')[0]
        else: 
            body_text = response.css('.js_header + div')[0]
        if body_text.css('.sc-1mep9y1-0 ::text').get():
            item['author'] = body_text.css('.sc-1mep9y1-0 ::text').get()
            item['author_link'] = body_text.css('.sc-1mep9y1-0 a').attrib['href']
        else:
            item['author'] = body_text.css('.sc-1jc3ukb-2 ::text').get()
        item['created_at'] = body_text.css('time').attrib['datetime']  

        # body extraction
        
        body_ps = body_text.css('.js_post-content p')


       
        # Extract body elements that are only text
        item['body_text'] = '\n'.join([''.join(p.css('::text').extract()) 
            for p in body_ps])
        # Extract links
        body_links = []
        for p in body_ps:
            body_links.extend(p.css('a[data-ga*="Embedded Url"]::attr(href)').extract())
        item['body_links'] = body_links
        
        yield item


        # Comments
#         comments = list()
#         blog_id = response.css('.top-tools').xpath('./ul/li/@data-blogid').extract()[0]
#         post_id = response.css('.post-dropdown-ct').xpath('./ul/@data-postid').extract()[0]
#         # We can only get 100 comments at a time
#         # But we can only specify the number of replies we want,
#         #   meaning we will get many more children per reply for each call
#         #   So we resort to getting just 5 replies per call
#         num_increment = 5
#         for i in xrange(0, int(num_reply), num_increment):
#             comments_url = 'http://earther.gizmodo.com/api/core/reply/' + \
#                                 '%s/replies?currentBlogId=' % (post_id) + \
#                                 '%s&startIndex=%s&maxReturned=' % (blog_id, i) + \
#                                 '%s&withLikeCounts=true' % (num_increment) + \
#                                 '&maxChildren=%s&approvedChildrenOnly=true' % (num_reply) + \
#                                 '&approvedStartersOnly=true&cache=true' 
#             # if parse_comments return nothing, then break
#             # append to comments otherwise
#             comm = self.parse_comments(comments_url)
#             if not comm:
#                 break
#             else:
#                 comments.extend(comm)

#         item['comments'] = comments

#     def parse_comments(self, comments_url):
#         """
#             takes:      url to get comments from
#             returns:    list of {'reply': r, 'children': c}
#         """
#         r = requests.get(comments_url)
#         comments = r.json()
        
#         if not comments:
#             return None

#         replyCount = comments['data']['directReplyCount']
#         comments = comments['data']['items']
#         commentsListObj = []
#         for c in comments:
#             commentsListObj.append(self.get_all_comment_objects(c))

#         return commentsListObj

#     def get_all_comment_objects(self, comment):
#         """
#             takes: list
#             return: dict of EartherComments
#         """
#         reply = comment['reply']
#         reply = self.get_comment_object(reply)
#         children = comment['children']['items']
#         childrenObj = []
#         for c in children:
#             childrenObj.append(self.get_comment_object(c))

#         return {'reply': reply, 'children': childrenObj}

#     def get_comment_object(self, comment):
#         """  
#             takes: dict
#             return: EartherComment
#         """
#         earther_comment = EartherComment()   
#         try:
#             # this needs to be fixed
#             earther_comment['parent_uid'] = comment['parentAuthorId']
#             earther_comment['parent_name'] = comment['replyMeta']['parentAuthor']['displayName']
#         except:
#             earther_comment['parent_uid'] = None
#             earther_comment['parent_name'] = None
#         earther_comment['length'] = comment['length']
#         earther_comment['likes'] = comment['likes']
#         earther_comment['author_uid'] = comment['author']['id']
#         earther_comment['author_name'] = comment['author']['displayName']
#         earther_comment['text'] = comment['plaintext']
#         earther_comment['time'] = comment['publishTimeMillis']
#         earther_comment['timezone'] = comment['timezone']
#         earther_comment['images'] = [c['uri'] for c in comment['images']]
#         earther_comment['videos'] = [v['src'] for v in comment['videos']]        
#         return earther_comment
