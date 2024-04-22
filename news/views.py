from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from .models import Story, Author, Agency
from django.core.serializers import serialize
from urllib.parse import urlparse, parse_qs
import datetime
import json


@csrf_exempt
def userLogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Author.objects.get(username=username)
                if user.password == password:
                    request.session['username'] = username
                    request.session['name'] = user.name
                    request.session.save()
                    return HttpResponse(status=200, content="Hello, {}!".format(user.username),
                                        content_type='text/plain')
                else:
                    return HttpResponse(status=401, content="Username or password invalid", content_type='text/plain')
            except Author.DoesNotExist:
                return HttpResponse(status=401, content="Username or password invalid", content_type='text/plain')
        else:
            return HttpResponse(status=401, content="Username or password invalid", content_type='text/plain')


@csrf_exempt
def userLogout(request):
    if 'username' in request.session:
        logout(request)
        return HttpResponse(status=200, content="You have been logged out successfully.", content_type='text/plain')
    else:
        return HttpResponse(status=401, content="You should log in first.", content_type='text/plain')


@csrf_exempt
def manageStory(request):
    if request.method == "POST":
        return createStory(request)
    elif request.method == "GET":
        return getStory(request)
    else:
        return HttpResponse(status=405, content="Can not manage stories", content_type='text/plain')


@csrf_exempt
def getStory(request):
    params = parse_qs(request.META["QUERY_STRING"])

    # Check the number of query parameters
    if len(params) != 3:
        return HttpResponse(status=404, content="The number of query parameters is wrong!", content_type="text/plain")

    # Check story category
    story_cat = params.get("story_cat", ["*"])[0]
    if story_cat != "*" and story_cat not in ("art", "pol", "tech", "trivia"):
        return HttpResponse(status=404,
                            content="Category is wrong! Right categories are 'art', 'pol', 'tech', 'trivia'.",
                            content_type='text/plain')

    # Check story region
    story_region = params.get("story_region", ["*"])[0]
    if story_region != "*" and story_region not in ("w", "uk", "eu"):
        return HttpResponse(status=404, content="Region is invalid. Right regions are 'w', 'uk', 'eu'.",
                            content_type='text/plain')

    # Check story date format
    story_date = params.get("story_date", ["*"])[0]
    if story_date != "*":
        try:
            date1 = datetime.datetime.strptime(story_date, "%d/%m/%Y")
        except ValueError:
            return HttpResponse(status=404, content="Date format is wrong. Date format should be 'DD/MM/YYYY'.",
                                content_type='text/plain')

    story_attr = {}
    if story_cat != "*":
        story_attr["category"] = story_cat
    if story_region != "*":
        story_attr["region"] = story_region
    if story_date != "*":
        story_attr["date__gte"] = date1

    try:
        find_story = Story.objects.filter(**story_attr)
        if not find_story.exists():
            return HttpResponse(status=404, content="Can not find the story.", content_type='text/plain')
    except Exception as e:
        return HttpResponse(status=404, content="Your search method is wrong: " + str(e), content_type='text/plain')

    serialised_filtered_stories = json.loads(serialize('json', find_story))

    story_array = []
    for story in serialised_filtered_stories:
        personal_story = {
            "key": story["pk"],
            "headline": story["fields"]["headline"],
            "story_cat": story["fields"]["category"],
            "story_region": story["fields"]["region"],
            "author": story["fields"]["author"],
            "story_date": story["fields"]["date"],
            "story_details": story["fields"]["details"]
        }
        story_array.append(personal_story)

    stories_json = {"stories": story_array}
    return HttpResponse(status=200, content=json.dumps(stories_json), content_type="application/json")


@csrf_exempt
def createStory(request):
    is_authenticated = request.session.get("username") is not None

    if is_authenticated:
        json_payload = json.loads(request.body.decode('utf-8'))
        print(json_payload)

        headline = json_payload['headline']
        category = json_payload['category']
        region = json_payload['region']
        details = json_payload['details']
        is_valid = True
        validation_messages = []

        if len(headline) > 64:
            is_valid = False
            validation_messages.append("Headline should be 64 chars or less! ")

        if region not in ("w", "uk", "eu"):
            is_valid = False
            validation_messages.append("Region should be 'w', 'uk' or 'eu'. ")

        if len(details) > 128:
            is_valid = False
            validation_messages.append("Details should be 128 characters or less. ")

        if category not in ("art", "pol", "tech", "trivia"):
            validation_messages.append("Category should be 'art', 'pol', 'tech' or 'trivia'. ")

        if is_valid:
            Story.objects.create(
                headline=headline,
                category=category,
                region=region,
                details=details,
                author=request.session["name"],
                date=datetime.datetime.now()
            )
            return HttpResponse(status=201)
        else:
            response = HttpResponse(
                status=503,
                content="Failed to create story.",
                content_type="text/plain"
            )
            response.status_code = 503
            return response
    else:
        response = HttpResponse("You should login first!")
        response.status_code = 503
        return response


@csrf_exempt
def deleteStory(request, key):
    is_authenticated = request.session.get("username") is not None

    if is_authenticated:
        try:
            story = Story.objects.get(id=key)
        except Story.DoesNotExist:
            return HttpResponse(status=404, content="Can not found this story.", content_type='text/plain')
        try:
            story.delete()
            return HttpResponse(status=200)
        except Exception:
            return HttpResponse(status=503, content="Sorry, fail to delete this story.", content_type='text/plain')
    else:
        return HttpResponse(status=403, content="You should login first!", content_type='text/plain')


@csrf_exempt
def for_agency(request):
    if request.method == 'POST':
        return register_agency(request)
    if request.method == 'GET':
        return all_agency(request)


@csrf_exempt
def register_agency(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=405)

    try:
        data = json.loads(request.body)
        agency_name = data.get("agency_name")
        url = data.get("url")
        agency_code = data.get("agency_code")

        if Agency.objects.filter(code=agency_code).exists():
            return HttpResponse("Agency code already exists.", status=400)

        agency = Agency.objects.create(name=agency_name, url=url, code=agency_code)

        return HttpResponse("Agency registered successfully.", status=201)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON format", status=400)
    except KeyError as e:
        return HttpResponse(f"Missing field: {e.args[0]}", status=400)
    except Exception as e:
        return HttpResponse(f"Failed to register agency. Error: {str(e)}", status=503)


def all_agency(request):
    if request.method == "GET":
        agencies = Agency.objects.all()
        agency_list = [
            {"agency_name": agency.name, "url": agency.url, "agency_code": agency.code}
            for agency in agencies
        ]
        return JsonResponse({"agency_list": agency_list})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
