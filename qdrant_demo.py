from synapseflow.qdrant_adapter import QdrantAdapter

def main():
    try:
        adapter = QdrantAdapter()
    except Exception as e:
        print('QdrantAdapter init failed (is qdrant-client installed and QDRANT_URL set?):', e)
        return
    adapter.upsert('demo_user', 'Visited Sanya beaches and loved Yalong Bay', {'tags':['travel']})
    adapter.upsert('demo_user', 'Booked hotel near Tianya Haijiao', {'tags':['travel']})
    print('Querying...')
    res = adapter.query('demo_user', 'Sanya')
    print('Results:', res)

if __name__ == '__main__':
    main()
