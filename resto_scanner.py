#imports
import json
from textblob import TextBlob
import os
import requests


# keyword lists
negative_keywords = [
"food poisoning",
"poison",
"sick",
"vomit",
"threw up",
"throw up",
"puke",
"nausea",
"diarrh",
"pain",
"cramp",
"bedridden",
"hospital",
"undercooked",
"raw",
"rotten",
"off meat",
"spoiled meat"
]

low_value_keywords = [
"small meal",
"small portion",
"small size",
"tiny meal",
"tiny portion",
"overpriced",
"bad value",
"low value",
"poor value",
"expensive",
"terrible",
"horrible",
"awful"
]

high_value_keywords = [
"large meal",
"large portion",
"large size",
"big portion",
"big meal",
"cheap",
"good value",
"great value",
"brilliant",
"excellent",
"incredible"
"inexpensive"
]

#scoring function
def score_restaurant(reviews, overall_rating):
	# set mean score to 0 before loop and flag
	mscore = 0
	flag = 0
	
	# loop review info getting
	for review in reviews:
		rating = review.get("rating", 0)
		time = review.get("relative_time_description", "Unknown")
		text = review.get("text", "").lower()
		
		# keyword checker
		kscore = 0
		words = text.split()
		for word in negative_keywords:
			if word in text:
				print("Red flagged:", word)
				flag += 1
				kscore -= 5
		vscore = 0
		for word in low_value_keywords:
			if word in text:
				print("Red flagged:", word)
				vscore -= 2
		for word in high_value_keywords:
			if word in text:
				print("Green flagged:", word)
				vscore += 1
		
		# run textblob
		blob = TextBlob(text)
		polarity = blob.sentiment.polarity
		
		# polarity score calc
		pscore = 0
		if polarity < -0.3:
			pscore -= 3
		elif polarity < -0.6:
			pscore -= 5
		elif polarity > 0.4:
			pscore += 2
		
		#display review info
		print("Time ago: ", time)
		print("Rating: ", rating)
		
		# keyword, polarity test
		print("Negative keyword score:", kscore)
		print("Polarity score:", pscore)
		print("Value score:", vscore)
		
		# calculate review total score
		tscore = kscore + pscore + vscore
		print("TOTAL SCORE:", tscore)
		print("")
	
		# calculate mean review score
		mscore += tscore
		
	# calculate complete score with google's
	if overall_rating is None:
		grating = 0
	elif overall_rating >= 4.5:
		grating = 2
	elif overall_rating >= 4:
		grating = 1
	elif overall_rating <= 2:
		grating = -2
	else:
		grating = 0

	mscore += grating
	
	# output final results
	print("Mean calculated review score:", mscore)
	print("Red flag number:", flag)
	return mscore, flag

API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual Google API key

# get user input
lat = input("Enter latitude: ")
lng = input("Enter longitude: ")
radius = input("Enter search radius in meters: ")

def search_nearby_restaurants(lat, lng, radius):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": API_KEY
    }
    
    response = requests.get(url, params=params)
    return response.json()

# show basic results
data = search_nearby_restaurants(lat,lng,radius)

for place in data.get("results", []):
    print(place.get("name"), "-", place.get("rating"))
    
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "fields": "name,rating,reviews",
        "key": API_KEY
    }
    
    response = requests.get(url, params=params)
    return response.json()
    

#creatu empty results list
results = []

if data.get("status") != "OK":
    print("Error:", data.get("status"))

else:
    for place in data.get("results", [])[:5]:
        name = place.get("name")
        place_id = place.get("place_id")
        overall_rating = place.get("rating")
        
        details = get_place_details(place_id)
        
        if details.get("status") == "OK":
            result = details.get("result", {})
            reviews = result.get("reviews", [])
            
            print("\nRestaurant:", name)
            print("Number of reviews:", len(reviews))
            
            for review in reviews:
                print("-", review.get("text"))
                
            # final score
            mscore, flag = score_restaurant(reviews, 	overall_rating)

            results.append({
                "name": name,
                "mean score": mscore,
                "red flags": flag
            })
print(results)

# Sort results by 'mean score' in descending order
top_restaurants = sorted(results, key=lambda x: x["mean score"], reverse=True)

# Pick top 3 (or fewer if less than 3 restaurants)
top_5 = top_restaurants[:5]

print("\n=== Top 5 Restaurants ===")
for i, r in enumerate(top_5, start=1):
    print(f"{i}. {r['name']}")
    print(f"   Mean Score: {r['mean score']}")
    print(f"   Red Flags: {r['red flags']}\n")