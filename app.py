from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

client = pymongo.MongoClient("mongodb+srv://ommundlik:omkarmundlik@cluster0.mzrghc0.mongodb.net/?retryWrites=true&w=majority")

db = client["FlipCartWebscrapping"]

collection1 = db["all_reviews"]
app = Flask(__name__)



@app.route("/", methods = ["GET"])
def home():
    return render_template("index.html")

@app.route("/review", methods=["POST" , "GET"] )
def Review():
    if request.method=="POST" :
        try :
            searchString = request.form["content"].replace(" ", "")
            logging.info(searchString)
            flipcart_url = "https://www.flipkart.com/search?q=" + searchString

            flipcart_url = uReq(flipcart_url)

            flipcart_html = bs(flipcart_url, "html.parser")

            big_boxes = flipcart_html.find_all("div", {"class" : "_1AtVbE col-12-12"})

            del big_boxes[0:3]
            # del big_boxes[23:]

            product_link = "https://www.flipkart.com" + big_boxes[0].div.div.div.a['href']
            logging.info(product_link)
            open_product = requests.get(product_link)
            open_product.encoding = 'utf-8'
            open_html = bs(open_product.text, "html.parser")

            comment_boxes = open_html.findAll("div", {"class" : "_16PBlm"})
            reviews = []
            for comment in comment_boxes:
                try :
                    product = searchString
                    logging.info(product)
                except Exception as e:
                    logging.error("product ka error ")
                    logging.error(e)

                try :
                    commentHead= comment.div.div.div.p.text
                except Exception as e:
                    commentHead = "No Head"
                    logging.error("commenthead")
                try :
                    name= comment.div.div.find_all("p", {"class" : "_2sc7ZR _2V5EHH"})[0].text
                except Exception as e:
                    name = "No Name"
                    logging.error("name ka error")
                    logging.error(e)

                try :
                    rating=  comment.div.div.div.div.text
                except Exception as e:
                    rating = "No Ratings"
                    logging.error(e)
                try:
                    custComment = comment.div.div.find_all("div" , {"class" : "t-ZTKy"})[0].div.div.text
                except Exception as e:
                    custComment = "No Comment"
                    logging.info("descript error")

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            try:
                collection1.insert_many(reviews)
            except Exception as e:
                logging.info("mongo error : " )
                logging.error(e)
            logging.info(f"logging my final reviews {reviews}")
            # logging.info(reviews)
            return render_template("result.html", reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return ("Something went wrong ")

    else:
        return render_template("index.html")
if(__name__ == '__main__'):
    app.run(host="0.0.0.0")
