from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def validate_data():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    total_count = collection.count_documents({})
    sample = collection.find().limit(5)

    print(f"✅ Total Events in DB: {total_count}")
    print("\n📄 Sample Events:\n")
    for event in sample:
        print(f"🎭 Show: {event.get('Show', 'N/A')}")
        print(f"📅 Date: {event.get('Date', 'N/A')} ⏰ {event.get('Time', 'N/A')}")
        print(f"📍 Theatre: {event.get('Theatre', 'N/A')}, Location: {event.get('Location', 'N/A')}")
        print(f"🖼️ Image: {event.get('Image Url', 'N/A')}")
        print(f"🔗 URL: {event.get('Link', 'N/A')}\n{'-' * 40}")

    client.close()

if __name__ == "__main__":
    validate_data()



