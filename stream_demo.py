import os, time, sys
from synapseflow.openai_integration import chat_stream

def main():
    prompt = 'Write a brief 150-word travel plan for Sanya including weather and two must-visit spots.'
    print('Streaming response:')
    collected = ''
    try:
        for chunk in chat_stream(prompt):
            print(chunk, end='', flush=True)
            collected += chunk
            time.sleep(0.01)
    except Exception as e:
        print('\nStreaming failed:', e)
        sys.exit(1)
    print('\n---\nFull text length:', len(collected))

if __name__ == '__main__':
    main()
