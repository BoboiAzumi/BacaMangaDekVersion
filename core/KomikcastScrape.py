from io import BytesIO, StringIO
import cfscrape
import base64
import json
from PIL import Image

from bs4 import BeautifulSoup
from sqlalchemy import null

class KomikcastScrape:

    def __init__(self):
        self.scrapper = cfscrape.create_scraper(delay=10)

    def encode(self, str):
        str = str.encode("ascii")
        str = base64.b64encode(str)
        str = str.decode("ascii")
        return str

    def decode(self, str):
        str = str.encode("ascii")
        str = base64.b64decode(str)
        str = str.decode("ascii")
        return str

    def scrape(self, url=""):
        url = "https://komikcast.site/{}".format(url)
        header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
        return self.scrapper.get(url, headers=header).content

    def scrapePost(self, data ,url=""):
        url = "https://komikcast.site/{}".format(url)
        
        header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
        return self.scrapper.post(url, headers=header, data=data).content

    def getIndexManga(self):
        content = self.scrape("daftar-komik/")
        parse = BeautifulSoup(content, "html.parser")

        parse = parse.find("div", attrs={'class', 'list-update'})
        parse = parse.find_all("div", attrs={'class', 'list-update_item'})

        Manga = []
        for i in parse:
            mangaType = i.find("span", attrs={'class', 'type'}).text
            judul = i.h3.text
            link = i.a["href"].replace('https://komikcast.site/komik','')
            link = "/informasi/"+link+"/"
            img = "/image/?data="+self.encode(i.img["src"])
            score = i.find("div", attrs={'class', 'numscore'}).text
        
            Manga.append({
                'judul': judul,
                'link' : link,
                'type': mangaType.strip(),
                'img' : img,
                'score':score
            })

        return Manga

    def getImage(self, str):
        link = self.decode(str)
        content = self.scrapper.get(link).content

        img = Image.open(BytesIO(content))
        image = BytesIO()
        img.save(image, "png", quality=1000)
        image.seek(0)
    
        img = null
        content = null
    
        return image

    def informasi(self, link):
        content = self.scrape("/komik/"+link)
        parser = BeautifulSoup(content, "html.parser")

        judul = parser.find("h1", attrs={"class","komik_info-content-body-title"}).text
        img =  "/image/?data="+self.encode(parser.find("img", attrs={"class", "komik_info-content-thumbnail-image"})["src"])
        altjudul = parser.find("span", attrs={"class", "komik_info-content-native"}).text
        genre = []
        rating = parser.find("strong").text.replace("Rating ", "")
        rilis = parser.find("span", attrs={"class", "komik_info-content-info-release"}).text.replace("Released:", "").strip()
        type_ = parser.find("span", attrs={"class", "komik_info-content-info-type"}).text.replace("Type:","").strip()
        update = parser.find("span", attrs={"class", "komik_info-content-update"}).text.replace("Updated on:", "").strip()
        other = []
        chapter = []
        sinopsis = parser.find("div", attrs={"class", "komik_info-description-sinopsis"}).text

        genres = parser.find_all("a", attrs={"class","genre-item"})
        others = parser.find_all("span", attrs={"class", "komik_info-content-info"})
        chapters = parser.find("ul", attrs={"class", "komik_info-chapters-wrapper"})
        chapters = parser.find_all("li", attrs={"class", "komik_info-chapters-item"})

        for i in genres:
            genre.append(i.text)

        for i in others:
            other.append(i.text)

        num = 1
        for i in chapters:
            chapteritem = {
                "chapter":i.find("a", attrs={"class", "chapter-link-item"}).text,
                "chapterlink":"/baca/?data="+self.encode(i.find("a", attrs={"class", "chapter-link-item"})["href"])+"&origin="+self.encode(link)+"&count="+str(num)+"&this="+i.find("a", attrs={"class", "chapter-link-item"}).text,
                "lastupdate":i.find("div", attrs={"class", "chapter-link-time"}).text.strip()
            }
            chapter.append(chapteritem)
            num += 1
        
        result = {
            "judul":judul,
            "altjudul":altjudul,
            "image":img,
            "genre":genre,
            "rating":rating,
            "rilis":rilis,
            "type":type_,
            "update":update,
            "sinopsis":sinopsis,
            "other":other,
            "chapter":chapter,
            "chapterlength":len(chapters)
        }
        return result
    
    def getMangaContent(self, link):
        link = self.decode(link).replace("https://komikcast.site/chapter/", "")
        content = self.scrape("chapter/"+link)
        parser = BeautifulSoup(content, "html.parser")
        image = []
        imageraw = parser.find_all("img", attrs={"class", "alignnone"})
        
        for i in imageraw:
            image.append("/image/?data="+self.encode(i["src"]))
        
        return image

    def populer(self):
        content = self.scrape("daftar-komik/?status=&type=&orderby=popular")
        parse = BeautifulSoup(content, "html.parser")

        parse = parse.find("div", attrs={'class', 'list-update'})
        parse = parse.find_all("div", attrs={'class', 'list-update_item'})

        Manga = []
        for i in parse:
            mangaType = i.find("span", attrs={'class', 'type'}).text
            judul = i.h3.text
            link = i.a["href"].replace('https://komikcast.site/komik','')
            link = "/informasi/"+link+"/"
            img = "/image/?data="+self.encode(i.img["src"])
            score = i.find("div", attrs={'class', 'numscore'}).text
        
            Manga.append({
                'judul': judul,
                'link' : link,
                'type': mangaType.strip(),
                'img' : img,
                'score':score
            })

        return Manga

    def search(self, judul):
        '''
        if judul == "":
            judul = "a"
        data = {"action":"searchkomik_komikcast_redesign",
        "orderby":"relevance",
        "per_page":200,
        "search=":judul
        }
        content = self.scrapePost(data, "wp-admin/admin-ajax.php")
        load = json.loads(content)
        print(len(load))
        return load
        '''

        content = self.scrape("/?s="+judul)
        parse = BeautifulSoup(content, "html.parser")
        
        parse = parse.find("div", attrs={'class', 'list-update'})
        parse = parse.find_all("div", attrs={'class', 'list-update_item'})

        Manga = []
        for i in parse:
            mangaType = i.find("span", attrs={'class', 'type'}).text
            judul = i.h3.text
            link = i.a["href"].replace('https://komikcast.site/komik','')
            link = "/informasi/"+link+"/"
            img = "/image/?data="+self.encode(i.img["src"])
            score = i.find("div", attrs={'class', 'numscore'}).text
        
            Manga.append({
                'judul': judul,
                'link' : link,
                'type': mangaType.strip(),
                'img' : img,
                'score':score
            })

        return Manga



if __name__ == "__main__":
    KS = KomikcastScrape()
    #print(getImage("aHR0cHM6Ly9pbWcuc3RhdGljYWxseS5pby9pbWcva2Nhc3QvY2RuLmtvbWlrY2FzdC5jb20vd3AtY29udGVudC9pbWcvSy9LYW5vam8tT2thcmlzaGltYXN1LzIzNy8wMDAucG5n"))
    
    print(KS.getIndexManga())