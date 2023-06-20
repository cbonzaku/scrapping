import logging
from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup, NavigableString
import re
import csv



titles = []
names = []
address = []
property_name=''
class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            "https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResultDetail?inquirytype=EntityName&directionType=Initial&searchNameOrder=SUN%203323020&aggregateId=domp-332302-972268cf-6af3-44ea-9e28-a633ab31f0dd&searchTerm=Sun&listNameOrder=SUN%203323020",

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")
        print({filename})


        with open(filename) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        div_corp = soup.find("div",{"class":"corporationName"})
        proprty=div_corp.find_all("p")
        global property_name
        property_name=proprty[1].text


        divs = soup.find_all("div", {"class": "detailSection"})
        div = divs[5]

        titls_Arr = div.find_all("span", string=re.compile("Title"))
        print(titls_Arr[1].text)

        for t in titls_Arr:
            b=mapppa(t.text.replace(u'\xa0',' '))
            titles.append(b)

        brs= div.find_all("br",recursive=False)

        for br in brs:
           if(isinstance(br.next_sibling,NavigableString) and br.next_sibling!='\n'):
               names.append({'name':br.next_sibling.strip('\n')})

        addr_divs=div.find_all("div")

        for d in addr_divs:
           s=d.find_all(text=True,recursive=False)
           address.append({'address': s[0].strip('\n')+s[1].strip('\n')})

        #names=[{"name":brs[3].next_sibling.strip()},{"name":brs[6].next_sibling.strip()},{"name":brs[9].next_sibling.strip()}]
        print(proprty[1].text,"\n",titles,"\n",names,"\n",address)



def mapppa(n):
    return {'title':n}


head=["Title","Name","address","Property Name"]

def generating_csv(p):
    with open('data.csv','w', newline='') as csvfile:
        writer= csv.writer(csvfile,delimiter='|',
                            quotechar=' ', quoting=csv.QUOTE_MINIMAL)


        writer.writerow(head)
        for i in range(len(names)):
            writer.writerow([titles[i]['title'],names[i]['name'],address[i]['address'],p])


if __name__ == "__main__":
    logging.getLogger('scrapy').propagate = False
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
    generating_csv(property_name)


