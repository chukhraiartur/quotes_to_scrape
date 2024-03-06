import json

import requests
from requests import Response
from parsel import Selector, SelectorList

from utils import WorkWithFiles


class QuotesToScrapeParser(WorkWithFiles):
    def __init__(self, url: str = 'https://quotes.toscrape.com') -> None:
        self.url = url
        self.headers = self.get_headers()
        self.response = self.get_response()
        self.save_to_html(self.response)

    def get_headers(self) -> dict:
        return {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

    def get_response(self) -> Response:
        return requests.get(url=self.url, headers=self.headers)

    def parse(self) -> list[dict]:
        data: list[dict] = []

        while True:
            selector: Selector = Selector(text=self.response.text)

            page_data = self.parse_page(selector)
            data.extend(page_data)

            if next_button := selector.css('.next'):
                url = self.url + next_button.css('a::attr(href)').get()
                self.response = requests.get(url=url, headers=self.headers)
            else:
                break

        return data

    def parse_page(self, selector: Selector) -> list[dict]:
        return [
            {
                'text': self.get_text(quote),
                'author': self.get_author(quote),
                'link': self.get_link(quote),
                'tags': self.get_tags(quote)
            }
            for quote in selector.css('.quote')
        ]

    def get_text(self, quote: Selector) -> str:
        return quote.css('.text::text').get().strip()[1:-1]

    def get_author(self, quote: Selector) -> str:
        return quote.css('[itemprop="author"]::text').get().strip()

    def get_link(self, quote: Selector) -> str:
        return self.url + quote.css('span a::attr(href)').get()

    def get_tags(self, quote: Selector) -> list[dict]:
        return [
            {
                'name': tag.css('::text').get().strip(),
                'link': self.url + tag.css('::attr(href)').get()
            }
            for tag in quote.css('.tags .tag')
        ]


def main() -> None:
    quotes_to_scrape_obj = QuotesToScrapeParser()
    data = quotes_to_scrape_obj.parse()

    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(len(data))


if __name__ == '__main__':
    main()
