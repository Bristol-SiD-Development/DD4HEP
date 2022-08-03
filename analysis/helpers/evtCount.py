events = [x for x in range(0, 24000)]
# print(f'events:{events}')
with open('anaj.txt', 'r') as f:
    for line in f:
        if "EVENT: " in line:
            evt = line.split()[-1]
            # print(f'evt: {evt}')
            events.remove(int(evt))

print(f'Missing events are {events}')
print(f'Missing {len(events)}')
