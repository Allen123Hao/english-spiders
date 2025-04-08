# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import time

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class CambridgeDictSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            retry_times = request.meta.get('retry_times', 0)
            
            # 如果达到最大重试次数，记录为最终失败
            if retry_times >= spider.settings.get('RETRY_TIMES', 3):
                spider.state_manager.mark_url_status(
                    request.url, 
                    spider._get_level(request.url),
                    'max_retries_reached',
                    retry_times
                )
            
            return self._retry(request, reason, spider) or response
        
        return response


class CustomDownloaderMiddleware:
    def __init__(self):
        self.last_request_time = time.time()

    def process_request(self, request, spider):
        # 实现自适应延迟
        current_time = time.time()
        time_passed = current_time - self.last_request_time
        if time_passed < spider.settings.get('DOWNLOAD_DELAY', 3):
            time.sleep(spider.settings.get('DOWNLOAD_DELAY', 3) - time_passed)
        
        self.last_request_time = time.time()
        
        # 添加自定义请求头
        request.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        })
        return None

    def process_response(self, request, response, spider):
        # 只记录失败的响应状态
        if response.status != 200:
            spider.state_manager.mark_url_status(
                request.url,
                spider._get_level(request.url),
                'failed'
            )
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SpiderProgressMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(s.item_scraped, signal=signals.item_scraped)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: %s' % spider.name)

    def item_scraped(self, item, spider):
        # 更新爬虫进度
        spider.state_manager.update_progress(
            processed_words=spider.state_manager.get_progress()['processed_words'] + 1
        )
