from scrapy.dupefilter import RFPDupeFilter


class DoNotFilter(RFPDupeFilter):

    def request_seen(self, request):
        return False
