from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def list_events(limit=None):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    query = collection.find().sort("Date", -1)
    if limit is not None:
        query = query.limit(limit)

    print(f"\n📢 Displaying {'all' if limit is None else limit} Broadway Events\n")
    for i, event in enumerate(query, start=1):
        print(f"{i}. {event.get('Show', 'N/A')} ({event.get('Date', 'N/A')} ⏰ {event.get('Time', 'N/A')})")
        print(f"   🎭 {event.get('Theatre', 'N/A')} - {event.get('Location', 'N/A')}")
        print(f"   🔗 {event.get('Link', 'N/A')}\n")

    client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="View Broadway Events from MongoDB")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--limit', type=int, help="Number of events to display (default: 10)")
    group.add_argument('--all', action='store_true', help="Show all events")
    args = parser.parse_args()

    list_events(limit=None if args.all else args.limit or 10)


