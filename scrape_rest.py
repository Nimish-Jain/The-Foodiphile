import requests
from bs4 import BeautifulSoup
import json

all_cookies = dict()
headers = dict()
zomato = list()
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"

def get_cookies():
	global all_cookies

	f = open("cookies.json","r")
	cookiedata = f.read()
	f.close() 

	cookiedata = json.loads(cookiedata)

	for i in cookiedata:
		name = i["name"]
		value = i["value"]
		all_cookies[name] = value

def connect_zomato():

	r = requests.get("https://www.zomato.com", cookies = all_cookies, headers=headers)
	if "Log out" in (r.text):
		print("Logged in!")
		print(" ")
	else:
		print("Not logged in!")
		print(" ")

def calculate_score(rating,offer_value):
	rating_score = (rating/0.1) * 1
	offer_score = offer_value * 2
    
	return (rating_score + offer_score)

def scrape_rest(pg_no):

	r = requests.get("https://www.zomato.com/ncr/order-food-online?delivery_subzone=290&page=%d"%pg_no, cookies = all_cookies, headers=headers)

	soup = BeautifulSoup(r.text,"html.parser")
	restaurants = soup.find_all("div",{"class" : "search-o2-card"})

	for restaurant in restaurants:
	
		rest_name = restaurant.findChildren("a",{"class" : "result-order-flow-title"})[0].text.strip()

		if (restaurant.findChildren("span",{"class":"rating-value"})):
			rest_rating = restaurant.findChildren("span",{"class":"rating-value"})[0].text.strip()
			rest_rating = float(rest_rating)	
		else:
			rest_rating = 0.0

		rest_offer = "No Offer"
		rest_offer_value = 0

		if(restaurant.findChildren("span",{"class":'offer-text'})):
			rest_offer = restaurant.findChildren("span",{"class":'offer-text'})[0].text.strip()

		if 'Rs.' in rest_offer: #rupee symbol
			rest_offer_value = rest_offer[rest_offer.index('Rs.')+1:rest_offer.index(" ")]
		elif "%" in rest_offer:
			rest_offer_value = int((rest_offer[0:rest_offer.index('%')]).strip())

		res_category=restaurant.findChildren("div",{'class':'grey-text'})[0].text.strip()

		rest_id = restaurant.get("data-res_id")

		all_rest = dict()
	
		rest_score = calculate_score(rating=rest_rating, offer_value = rest_offer_value)


		all_rest['rest_name'] = rest_name
		all_rest['rest_id'] = rest_id
		all_rest['rest_rating'] = rest_rating
		all_rest['rest_offer'] = rest_offer
		all_rest['res_category'] = res_category
		all_rest['rest_score'] = rest_score

		zomato.append(all_rest)

		sorted_rest = sorted(zomato,key = lambda i: i['rest_score'],reverse=True)

	return sorted_rest

get_cookies()
connect_zomato()

for i in range(1,5):
	restaurants = scrape_rest(i)

for restaurant in restaurants:
	if(restaurant['rest_score']>0):
		print("Res name - %s"%restaurant['rest_name'])
		print("Res id - %s"%restaurant['rest_id'])
		print("Res rating - %s"%restaurant['rest_rating'])
		print("Res offer - %s"%restaurant['rest_offer'].replace('\u20b9','Rs.'))
		print("Res category - %s"%restaurant['res_category'])
		print("Res score - %s"%restaurant['rest_score'])
		print(" ")
		print(" ")

	else:
		print("All other restaurants are unrated!")
		break