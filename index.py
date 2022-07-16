from flask import Flask, render_template, send_file, request
from core.KomikcastScrape import KomikcastScrape
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

App = Flask(__name__)
KS = KomikcastScrape()

@App.errorhandler(404)
def error404(e):
    return render_template('404.html')

@App.route("/")
def root():
    return render_template("index.html", Manga=KS.getIndexManga(), info="")

@App.route("/about/")
def about():
    return render_template("about.html")

@App.route("/informasi/<string:judul>/")
def informasi(judul):
    data = KS.informasi(judul)
    return render_template('informasi.html', data=data)

@App.route("/image/")
def image():
    base64 = request.args.get('data')
    return send_file(KS.getImage(base64), mimetype="image/png")

@App.route("/baca/")
def baca():
    datalink = request.args.get('data')
    originlink = KS.decode(request.args.get('origin'))
    thischap = request.args.get('this')
    informasi = KS.informasi(originlink)
    allchapter = informasi['chapter']
    count = request.args.get('count')
    content = KS.getMangaContent(datalink)

    return render_template('baca.html',thischap = thischap, 
    allchapter = allchapter, count=int(count), lenchapter=len(allchapter),
    judul = informasi["judul"], originlink = "/informasi/"+originlink, content = content)

@App.route("/populer/")
def populer():
    return render_template("index.html", Manga=KS.populer(), info="")

@App.route("/search/")
def search():
    judul = request.args.get('judul')
    return render_template("index.html", Manga=KS.search(judul), info=judul)

if __name__ == "__main__":
    App.run(host="0.0.0.0",port=80, debug=True)