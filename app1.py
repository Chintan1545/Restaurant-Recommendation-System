from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Restaurant Recommendation API")

# Load dataset
lko_rest = pd.read_csv("./food1.csv")


# ------------------ ML LOGIC (UNCHANGED) ------------------

def fav(lko_rest1):
    lko_rest1 = lko_rest1.reset_index()

    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(lko_rest1['highlights'])

    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    sim = list(enumerate(cosine_sim[0]))
    sim = sorted(sim, key=lambda x: x[1], reverse=True)
    sim = sim[1:11]

    indices = [i[0] for i in sim]

    final = lko_rest1.iloc[indices]
    return final


def rest_rec(cost, people=2, min_cost=0, cuisine=[], Locality=[], fav_rest=""):
    cost = cost + 200

    x = cost / people
    y = min_cost / people

    lko_rest1 = lko_rest[lko_rest['locality'] == Locality[0]]

    for i in range(1, len(Locality)):
        temp = lko_rest[lko_rest['locality'] == Locality[i]]
        lko_rest1 = pd.concat([lko_rest1, temp]).drop_duplicates(subset='name')

    lko_rest1 = lko_rest1[
        (lko_rest1['average_cost_for_one'] <= x) &
        (lko_rest1['average_cost_for_one'] >= y)
    ]

    lko_rest1['Start'] = lko_rest1['cuisines'].str.find(cuisine[0])
    lko_rest_cui = lko_rest1[lko_rest1['Start'] >= 0]

    if fav_rest:
        favr = lko_rest[lko_rest['name'] == fav_rest]
        combined = pd.concat([favr, lko_rest_cui])
        combined.drop(columns=['Start'], inplace=True, errors='ignore')
        result = fav(combined)
    else:
        result = lko_rest_cui.sort_values('scope', ascending=False).head(10)

    return result


def calc(max_price, people, min_price, cuisine, locality):
    rest_sugg = rest_rec(
        max_price,
        people,
        min_price,
        [cuisine],
        [locality]
    )

    rest_list = rest_sugg[
        ['name', 'address', 'locality', 'timings',
         'aggregate_rating', 'url', 'cuisines']
    ]

    return rest_list.to_dict(orient="records")


# ------------------ FASTAPI SCHEMA ------------------

class SearchRequest(BaseModel):
    people: int
    min_price: int
    max_price: int
    cuisine: str
    locality: str


# ------------------ API ROUTES ------------------

@app.get("/")
def home():
    return {"message": "Restaurant Recommendation API is running 🚀"}


@app.post("/search")
def search(data: SearchRequest):
    result = calc(
        data.max_price,
        data.people,
        data.min_price,
        data.cuisine,
        data.locality
    )
    return {"restaurants": result}
