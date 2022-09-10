from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
import requests
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs

app = Flask(__name__)


# this function is to render the homepage
@app.route('/', methods=['GET'])
@cross_origin()
def homePage():
    return render_template("index.html")


# main function which scraps and returns the list of all the reviews
@app.route('/review', methods=['GET', 'POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            # extract the search keyword from  the UI
            searchString = request.form['content'].replace(" ", "")

            # generating the url
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            # interacting and scraping the result page
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()

            # now we parse the content and apply filters to extract data
            flipkartPage = bs(flipkartPage, 'html.parser')

            # extracting the boxes from the search results
            bigboxes = flipkartPage.findAll("div", {"class": '_1AtVbE col-12-12'})
            del bigboxes[0:2]

            # getting the first search result
            box = bigboxes[0]

            # getting the details page link of the first search result
            prodLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(prodLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, 'html.parser')

            # extracting the comment boxes from the review section
            commentboxes = prod_html.find_all("div", {'class': '_16PBlm'})
            filename = searchString + ".csv"
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw = open(filename, 'w')
            fw.write(headers)
            reviews = []

            # now we loop through the comment boxes extracted
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = "No Name"
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = "No Rating"
                try:
                    commonHead = commentbox.div.div.div.p.text
                except:
                    commonHead = "No Common Heading"
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)
                mydict = {
                    "Product": searchString,
                    "Name": name,
                    "Rating": rating,
                    "CommonHead": commonHead,
                    "Comment": custComment
                }
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print("Something went wrong")
            return 'something went wrong'
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
