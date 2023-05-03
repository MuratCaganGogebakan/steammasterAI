import json

def split_reviews(reviews):
    splitted_reviews = []
    for review in reviews:
        while len(review) > 2000:
            splitted_reviews.append(review[:2000])
            review = review[2000:]
        splitted_reviews.append(review)
    return splitted_reviews

def aggregate_reviews(reviews):
    combined_reviews = []
    for review in reviews:
        if combined_reviews == []:
            combined_reviews.append(review)
        elif len(combined_reviews[-1]) < 1500 and (len(combined_reviews[-1]) + len(review)) < 2000:
            combined_reviews[-1] += review
        elif len(combined_reviews[-1]) > 1500:
            combined_reviews.append(review)
    return combined_reviews

# Read reviews from json file
def read_reviews():
    with open('reviews.json', 'r') as f:
        reviewsdict = json.load(f)
    return reviewsdict

def chunk_reviews(reviewsdict):
    chunks = []
    for game in reviewsdict:
        #print(game)
        combined_reviews = aggregate_reviews(split_reviews(reviewsdict[game]))
        for review in combined_reviews:
            review = game + ": " + review
            chunks.append(review)
    return chunks

if __name__ == "__main__":
    # output chunks as text file
    chunks = chunk_reviews(read_reviews())
    with open('chunks.txt', 'w') as f:
        for chunk in chunks:
            f.write(chunk + '\n')
    
