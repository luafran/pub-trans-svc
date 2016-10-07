"""
Agency entity
"""


class Agency(object):  # pylint: disable=too-few-public-methods

    def __init__(self, tag, title, region_title):
        self.tag = tag
        self.title = title
        self.region_title = region_title
