
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import multiprocessing
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from flask import Flask, render_template, request, redirect,url_for
from youtubedat import *
import pandas as pd
from wordcloud import WordCloud


app = Flask(__name__)
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
  # Here the user agent is for Edge browser on windows 10. You can find your browser user agent from the above given link.
@app.route('/')
def home():
    return render_template('main.html')

# @app.route('/ecommerce' , methods = ['GET', 'POST'])
# def ecommerce():
#     if(request.method=='POST'):
#       query=request.form.get('searchquery')
#       return redirect(url_for("search",query=query))
#     return render_template('index.html')

@app.route('/ecommerce', methods=['GET', 'POST'])
def ecommerce():
    if request.method == 'POST':
        query = request.form.get('searchquery')
        if query:  
            return redirect(url_for("search", query=query))  
    
    return render_template('index.html')

@app.route('/youtube', methods=['GET', 'POST'])
def youtube():
  if request.method == 'POST':
    query = request.form.get('searchquery')
    channel_id=get_channel_id(query)
    uploads_playlist_id = get_uploads_playlist_id(channel_id)
    if uploads_playlist_id:
        video_ids = get_all_video_ids(uploads_playlist_id)
        videos = get_video_details(video_ids)
    return render_template('videos.html',data=videos)
  return render_template('youtube.html')



@app.route('/YTvideoanalysis/<id>')
def analysisyoutube(id):
    # Fetch YouTube comments
    comments = fetch_comments(id)

    # Perform sentiment analysis
    comments[["Sentiment", "Sentiment Score"]] = comments["text"].apply(lambda x: pd.Series(analyze_sentiment(str(x))))

    # Convert DataFrame to HTML
    comments_html = comments.to_html(classes='dataframe', index=False)

    # ------------------- Plot 1: Sentiment Distribution -------------------
    plt.figure(figsize=(8, 5))
    sentiment_counts = comments["Sentiment"].value_counts()
    sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette=["red", "blue", "green"])
    plt.title("Sentiment Distribution of YouTube Comments")
    plt.xlabel("Sentiment")
    plt.ylabel("Number of Comments")

    img_io1 = io.BytesIO()
    plt.savefig(img_io1, format='png', bbox_inches='tight')
    img_io1.seek(0)
    encoded_img1 = base64.b64encode(img_io1.getvalue()).decode('utf-8')
    plt.close()

    # ------------------- Plot 2: Average Comment Likes per Sentiment -------------------
    if "like_count" in comments.columns:
        sentiment_vs_likes = comments.groupby("Sentiment")["like_count"].mean()

        plt.figure(figsize=(8, 5))
        sns.barplot(x=sentiment_vs_likes.index, y=sentiment_vs_likes.values, palette=["red", "blue", "green"])
        plt.title("Average Comment Likes per Sentiment")
        plt.xlabel("Sentiment")
        plt.ylabel("Average Comment Likes")

        img_io2 = io.BytesIO()
        plt.savefig(img_io2, format='png', bbox_inches='tight')
        img_io2.seek(0)
        encoded_img2 = base64.b64encode(img_io2.getvalue()).decode('utf-8')
        plt.close()
    else:
        encoded_img2 = None

    # ------------------- Plot 3: Sentiment Trends Over Time -------------------
    comments["published_at"] = pd.to_datetime(comments["published_at"])
    comments["date"] = comments["published_at"].dt.date

    sentiment_over_time = comments.groupby(["date", "Sentiment"]).size().unstack()

    plt.figure(figsize=(12, 6))
    sentiment_over_time.plot(kind="line", marker="o")
    plt.title("📈 Sentiment Trends Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Comments")
    plt.xticks(rotation=45, ha='right') 
    plt.legend(title="Sentiment")
    plt.grid()

    img_io3 = io.BytesIO()
    plt.savefig(img_io3, format='png', bbox_inches='tight')
    img_io3.seek(0)
    encoded_img3 = base64.b64encode(img_io3.getvalue()).decode('utf-8')
    plt.close()

    # ------------------- Word Cloud: Positive Comments -------------------
    positive_text = " ".join(comments[comments["Sentiment"] == "Positive"]["text"].dropna())

    if positive_text.strip():
        positive_wc = WordCloud(width=500, height=300, background_color="white").generate(positive_text)

        plt.figure(figsize=(6, 4))
        plt.imshow(positive_wc)
        plt.axis("off")
        plt.title("Positive Comments Word Cloud")

        img_io4 = io.BytesIO()
        plt.savefig(img_io4, format='png', bbox_inches='tight')
        img_io4.seek(0)
        encoded_img4 = base64.b64encode(img_io4.getvalue()).decode('utf-8')
        plt.close()
    else:
        encoded_img4 = None

    # ------------------- Word Cloud: Negative Comments -------------------
    negative_text = " ".join(comments[comments["Sentiment"] == "Negative"]["text"].dropna())

    if negative_text.strip():
        negative_wc = WordCloud(width=500, height=300, background_color="black").generate(negative_text)

        plt.figure(figsize=(6, 4))
        plt.imshow(negative_wc)
        plt.axis("off")
        plt.title("Negative Comments Word Cloud")

        img_io5 = io.BytesIO()
        plt.savefig(img_io5, format='png', bbox_inches='tight')
        img_io5.seek(0)
        encoded_img5 = base64.b64encode(img_io5.getvalue()).decode('utf-8')
        plt.close()
    else:
        encoded_img5 = None

    return render_template(
        'analysis.html',
        data=comments_html,
        encoded_img1=encoded_img1,
        encoded_img2=encoded_img2,
        encoded_img3=encoded_img3,
        encoded_img4=encoded_img4,  # Positive Word Cloud
        encoded_img5=encoded_img5   # Negative Word Cloud
    )

  


  


    
# @app.route('/', methods = ['GET', 'POST'])
# def home():
#   if(request.method=='POST'):
#     query=request.form.get('searchquery')
#     return redirect(url_for("search",query=query))
#   return render_template('index.html')
  
# searches
# @functools.lru_cache(maxsize=None)
def slate(query):
  query=query.strip().replace(" ","+")
  slate_url=f"https://slatehash.com/search?q={query}"
  slate_url_content=requests.get(slate_url)
  
  slate=[]
   
  slate_soupdata=BeautifulSoup(slate_url_content.content,'lxml')
  slate_data=slate_soupdata.findAll('li',{'class':'grid__item'})
  for single_data in slate_data:
    try:
      title=single_data.find('h3',{'class':'card__heading'}).text
    except:
      None
    try:
      off=single_data.find('span',{'class':'badge--bottom-left'}).text
    except:
      None
    try:
      link="https://slatehash.com/"+str(single_data.find('a',{'class':'full-unstyled-link'})['href'])
    except:
      None
    try:
      image=single_data.find('img')
    except:
      None
    try:
      image="https:"+str(image.get('src'))
    except:
      None
    price=single_data.findAll('span',{'class':'money'})
    oldprice=price[1].text if price[0] else ""
    newprice=price[0].text if price[1] else ""
    slate.append({
      "title":title.strip(),
      "link":link,
      "image":image,
      "off":off.strip(),
      "newprice":newprice,
      "oldprice":oldprice
    })
  return slate
  
# @functools.lru_cache(maxsize=None)
def snapdeal(query):
  query=query.strip().replace(" ","%20")
  URL = f"https://www.snapdeal.com/search?keyword={query}&sort=rlvncy"
  snapdeal_url_content= requests.get(url=URL,headers=headers)
  snapdeal_soup_total=BeautifulSoup(snapdeal_url_content.content,'lxml')
  snapdeal_product_wrapper=snapdeal_soup_total.findAll('div',{'class':'product-tuple-listing'})
  snapdeal=[]
  for wrapper in snapdeal_product_wrapper:
    title=wrapper.find('p',{'class':'product-title'})['title']
    # rating 
    try:
      rating=wrapper.find('p',{'class':'product-rating-count'}).text
    except:
      rating=""
    # off 
    try:
      off=wrapper.find('div',{'class':'product-discount'})
      off=off.find('span').text
    except:
      off=""
    # old_price 
    try:
      old_price=wrapper.find('span',{'class':'product-desc-price'}).text
    except:
      old_price=""
    # new_price 
    try:
      new_price=wrapper.find('span',{'class':'product-price'}).text
    except:
      new_price=""
    # link
    link=wrapper.find('a',{'class':'dp-widget-link'})['href']
    # image
    image=wrapper.find('picture',{'class':'picture-elem'})
    image=image.find('source')['srcset']
    data={
      "link":link,
      "title":title,
      "old_price":old_price,
      "new_price":new_price,
      "rating":rating,
      "off":off,
      "image":image
    }
    snapdeal.append(data)
  return snapdeal

# @functools.lru_cache(maxsize=None)
# def flipkart(query):
#   query=query.strip().replace(" ","+")
#   flipkart_url=f"https://www.flipkart.com/search?q={query}&page=1"
#   flipkart_http_obj=urlopen(flipkart_url)
#   flipkart_webdata_total=flipkart_http_obj.read()
  
#   flipkart=[]
  
#   def flipkart_details_function(flipkart_product_url):
#     flipkart_http_obj_main=urlopen(flipkart_product_url)
#     flipkart_webdata_total_main=flipkart_http_obj_main.read()
#     flipkart_soupdata_main=BeautifulSoup(flipkart_webdata_total_main,'html.parser')
#     # getting title
#     title=flipkart_soupdata_main.find('span',{'class':'B_NuCI'})
#     title=title.text
#     # getting new price
#     try:
#       new_price=flipkart_soupdata_main.find('div',{'class':'_30jeq3'})
#       new_price=new_price.text
#     except:
#       new_price=None
#     # getting old price
#     try:
#       old_price=flipkart_soupdata_main.find('div',{'class':'_3I9_wc'})
#       old_price=old_price.text
#     except:
#       old_price=None
#     # getting off 
#     try:
#       off=flipkart_soupdata_main.find('div',{'class':'_3Ay6Sb'})
#       off=off.text
#     except:
#       off=None
#     # getting stars
#     try:
#       stars=flipkart_soupdata_main.find('div',{'class':'_3LWZlK'})
#       stars=stars.text
#     except:
#       stars=None
#     # getting rating and reviews
#     try:
#       ratings=flipkart_soupdata_main.find('span',{'class':'_2_R_DZ'})
#       ratings=ratings.text
#     except:
#       ratings=None
  
#     # details
#     details_main={"title":title,
#                   "new_price":new_price,
#                   "old_price":old_price,
#                   "stars":stars,
#                   "rating":ratings,
#                   "off":off}
#     return details_main
  
  
#   # try:
#   #   for pagenumber in range(2,4):
#   #     flipkart_url=f"https://www.flipkart.com/search?q={query}&page={pagenumber}"
#   #     flipkart_http_obj=urlopen(flipkart_url)
#   #     flipkart_webdata=flipkart_http_obj.read()
#   #     flipkart_webdata_total+=flipkart_webdata
#   # except:
#   #   pass
    
#   flipkart_soupdata=BeautifulSoup(flipkart_webdata_total,'html.parser')
#   flipkart_containers=flipkart_soupdata.findAll('div',{'class':'_13oc-S'})
#   for container in flipkart_containers:
#     try:
#       flipkart_productlink_data=container.findAll('div',{'class':'_4ddWXP'})
#       for i in range(4):
#         flipkart_productlink=flipkart_productlink_data[i]
#         flipkart_productlink=flipkart_productlink.find('a')['href']
#         flipkart_productlink="https://www.flipkart.com"+str(flipkart_productlink)
#         try:
#           flipkart_image=flipkart_productlink_data[i].find('img')
#           flipkart_image=flipkart_image.get('src')
#         except:
#           flipkart_image=None
#         details=flipkart_details_function(flipkart_productlink)
#         details=details | {"image":flipkart_image,"link":flipkart_productlink}
#         flipkart.append(details)
#     except:
#       try:
#         flipkart_productlink_data=container.findAll('div',{'class':'_1xHGtK'})
#         for i in range(4):
#           flipkart_productlink=flipkart_productlink_data[i]
#           flipkart_productlink=flipkart_productlink.find('a')['href']
#           flipkart_productlink="https://www.flipkart.com"+str(flipkart_productlink)
#           try:
#             flipkart_image=flipkart_productlink_data[i].find('img')
#             flipkart_image=flipkart_image.get('src')
#           except:
#             flipkart_image=None
#           details=flipkart_details_function(flipkart_productlink)
#           details=details | {"image":flipkart_image,"link":flipkart_productlink}
#           flipkart.append(details)
#       except:
#           # for 1 row datas like laptops
#           flipkart_productlink=container.find('a')['href']
#           flipkart_productlink="https://www.flipkart.com"+str(flipkart_productlink)
#           try:
#             flipkart_image=container.find('img')
#             flipkart_image=flipkart_image.get('src')
#           except:
#             flipkart_image=None
#           details=flipkart_details_function(flipkart_productlink)
#           details=details | {"image":flipkart_image,"link":flipkart_productlink}
#           flipkart.append(details)
#   return flipkart
  
# @app.route("/search/<query>")
# def search(query):
#   # pool = multiprocessing.Pool(processes=3)
  
#   # result1 = pool.apply_async(flipkart,(query,))
#   # result2 = pool.apply_async(snapdeal,(query,))
#   # result3 = pool.apply_async(slate,(query,))
  
#   # flipkart_data=result1.get()
#   # snapdeal_data=result2.get()
#   # slatehouse_data=result3.get()
#   # flipkart_data=flipkart(query)
#   snapdeal_data=snapdeal(query)
#   slatehouse_data=slate(query)
#   return render_template('products.html', snapdeal_data=snapdeal_data, slatehouse_data=slatehouse_data)
@app.route("/search/<query>")
def search(query):
    snapdeal_data = snapdeal(query)
    slatehouse_data = slate(query)
    return render_template('products.html', snapdeal_data=snapdeal_data, slatehouse_data=slatehouse_data)



@app.route('/application')
def application():
  return render_template('maintainence.html',message="Mobile App Under Development")

@app.route('/privacy')
def privacy():
  return render_template('privacy.html')

@app.route('/terms')
def terms():
  return render_template('terms.html')

@app.route('/about')
def about():
  return render_template('about.html')

# invalid url error
@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'),404

# internal server error
@app.errorhandler(500)
def server_error(e):
  return render_template('maintainence.html',message="Internal Server Error"),500


app.run(host='0.0.0.0', port=81,debug=True)