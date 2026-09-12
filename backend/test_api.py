import urllib.request
import json

r = urllib.request.urlopen("http://127.0.0.1:8000/api/employees/")
data = json.loads(r.read())
print(f"Employees: {len(data)}")
for e in data:
    print(f"  - {e['name']} ({e['department']})")

r2 = urllib.request.urlopen("http://127.0.0.1:8000/api/tasks/")
tasks = json.loads(r2.read())
print(f"\nTasks: {len(tasks)}")
for t in tasks:
    print(f"  - [{t['priority']}] {t['title']}")

print("\n[OK] API is working! Open http://127.0.0.1:8000/docs in your browser.")
