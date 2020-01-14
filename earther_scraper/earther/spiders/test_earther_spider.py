"""
Use this crawler to crawl a specified article path from earther,
this is for testing.
"""


import scrapy
import requests
import math

from earther.items import EartherItem #, EartherComment

PATH = "/smoke-from-australia-s-horrific-wildfires-as-seen-from-1840789029"

class TestEartherSpider(scrapy.Spider):
    name = "earther"
    allowed_domains = ["earther.gizmodo.com"]
    start_urls = [
        f"http://earther.gizmodo.com{PATH}",
    ]

    def parse(self, response):
        item = EartherItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get()
        item['twitter_url'] = response.css('meta[name="twitter:url"]').attrib['content']
        item['image']  = response.css('meta[property="og:image"]').attrib['content']

        k = response.css('meta[name="keywords"]').attrib['content']
        keywords = list(set(map(str.strip, k.split(','))))
        item['keywords'] = keywords
        
        item['description'] = response.css('meta[name="description"]').attrib['content']
        
        # this only sometimes works
        item['author'] = response.css('main .sc-1mep9y1-0 ::text').get()
        item['author_link'] = response.css('main .sc-1mep9y1-0 a').attrib['href']
        
        item['created_at'] = response.css('main time').attrib['datetime']        
        item['num_like']  = response.css('div[title] span::text').get()
        item['num_reply'] = response.css('a[data-ga*="Comment count"] span::text').get()
        
        # body extraction
        
        body_ps = response.css('main .js_post-content p')
        # Extract body elements that are only text
        item['body_text'] = '\n'.join([''.join(p.css('::text').extract()) 
            for p in body_ps])
        # Extract links
        body_links = []
        for p in body_ps:
            body_links.extend(p.css('a[data-ga*="Embedded Url"]::attr(href)').extract())
        item['body_links'] = body_links
        
        yield item

"""
        body = response.css('.post-content').xpath('./p')
        img_idx = []
        vid_idx = []
        text_idx = []
        for idx, b in enumerate(body):
            if b.re('has-image'):
                img_idx.append(idx)
            elif b.re('has-video'):
                vid_idx.append(idx)
            else:
                text_idx.append(idx)
        body_img = [body[i].xpath('.//img/@src').extract() for i in img_idx]
        # body_vid = [body[i] for i in vid_idx]
        body_text = [' '.join(body[i].xpath('.//text()').extract()) for i in text_idx]
        item['body_imgs'] = body_img
        item['body_text'] = body_text

        num_like = response.css('.js_like_count').xpath('./text()').extract()[0]
        num_reply = response.css('.js_reply-count').xpath('./text()').extract()[0]
        item['num_reply'] = num_reply
        item['num_like'] = num_like
"""
        # Comments
#         comments = list()
#         blog_id = response.css('.top-tools').xpath('./ul/li/@data-blogid').extract()[0]
#         post_id = response.css('.post-dropdown-ct').xpath('./ul/@data-postid').extract()[0]
        # We can only get 100 comments at a time
        # But we can only specify the number of replies we want,
        #   meaning we will get many more children per reply for each call
        #   So we resort to getting just 5 replies per call
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
#                 print('Error loading comments: ', comments_url)
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

