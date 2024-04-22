from django.test import Client

client = Client()
response = client.get('/api/stories', {'story_cat': '*', 'story_region': '*', 'story_date': '*'})
print(response.status_code)
print(response.content)
