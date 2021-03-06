from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpRequest
from django.core.context_processors import csrf
from django.template.context_processors import request
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.db.models import Q

from datetime import datetime,timedelta
from string import join,split
from random import randint
from urllib2 import urlopen
from contextlib import closing
from ipware.ip import get_ip
from decimal import Decimal


import geocoder
import cgi
import json
import math
import sys
import requests

from datetime import datetime,time, date
from .forms import VerificationForm, PasswordChangeForm
from carpool.models import User, UserProfile, Post,Profileposts,Block,Location,Car,Trip,TripRequest
from carpool.forms import RegistrationForm,UpdateProfileForm

# utility functions

def get_ip_add():
    """
    returns the ip address of the client
    :return:the ip address of the client
    """
    r = requests.get(r'http://jsonip.com')
    ip= r.json()['ip']
    print 'Your IP is', ip
    return ip

def get_location(ip):
    """
    determines location using http:freegeoip.net API

    :param ip(str):a valid global ipv4 address
    :return:location_data(dict): a JSON format containing necessary attributes of a location based on the given ip

            Example:

            {
            u'city': u'', u'region_code': u'',
            u'region_name': u'', u'ip': u'2607:f8b0:4006:80f::200e',
            u'time_zone': u'', u'longitude': -98.5,
            u'metro_code': 0, u'latitude': 39.76,
            u'country_code': u'US', u'country_name': u'United States',
            u'zip_code': u''
            }


    """
    #CAPS
    #url = 'http://freegeoip.net/json/'
    url="http://geoip.nekudo.com/api/"
    ip="116.58.202.54"
    url += str(ip)
    print(url)
    try:
        with closing(urlopen(url)) as response:
            location_data = json.loads(response.read())
            print(location_data)

            return location_data

    except:
        print("Location could not be determined automatically")



def getStatus(c):
        trip_status_choices = {
        'a': 'approved',
        'd': 'disapproved',
        'o': 'other',
        'p': 'pending',
        's': 'suspended'
    }

        return trip_status_choices[c];

def get_ip_address(request):
    """
    returns the remote address of the client request


    :param request: a Request variable,whose remote address has to be determined
    :return: a string representing a valid ipv4 address
    """

    ip_address = get_ip(request)
    if ip_address is not None:
        print "we have an IP address for user"
    else:
        print "we don't have an IP address for user"
    return ip_address


def get_proximity_range(location_data,x_range,y_range):
    """
    returns the range of the latitude and longitude in between which a user can see others posts

    :param location_data:a JSON format dictionary containing necessary attributes of a location based on the given ip

            Example:

            {
            u'city': u'', u'region_code': u'',
            u'region_name': u'', u'ip': u'2607:f8b0:4006:80f::200e',
            u'time_zone': u'', u'longitude': -98.5,
            u'metro_code': 0, u'latitude': 39.76,
            u'country_code': u'US', u'country_name': u'United States',
            u'zip_code': u''
            }

    :param x_range:range of longitude
    :param y_range:range of latitude
    :return:a dictionary containing the [min,max] of [latitude,logitude]

            example:
                {
                'min_lat':-22.36 ,
                'max_lat':86.35,
                'min_long':-98.23,
                'max_long':127.12
                }

    """
    proximity_range = dict(min_lat=-90.00, max_lat=90.00, min_long=-180.00, max_long=180.00)

    proximity_range['min_lat'] = math.ceil(location_data['latitude']-y_range)
    proximity_range['max_lat'] = math.ceil(location_data['latitude']+y_range)
    proximity_range['min_long'] = math.ceil(location_data['longitude']-x_range)
    proximity_range['max_long'] = math.ceil(location_data['longitude']+x_range)

    if proximity_range['min_lat'] < -90.00:
        proximity_range['min_lat'] = -90.00
    if proximity_range['max_lat'] > 90.00:
        proximity_range['max_lat'] = 90.00
    if proximity_range['min_long'] < -180.00:
        proximity_range['min_long'] = -180.00
    if proximity_range['max_long'] > 180.00:
        proximity_range['max_long'] = -90.00

    return proximity_range


def get_valid_range(request,x_range,y_range):
    """
    returns the proximity range of the client

    :param request:a Request variable
    :param x_range:a double,range of longitude
    :param y_range:a double,range of latitude
    :return:proximity_range_client(dict):
        a dictionary containing the [min,max] of [latitude,logitude]

            example:
                {
                'min_lat':-22.36 ,
                'max_lat':86.35,
                'min_long':-98.23,
                'max_long':127.12
                }
    """

    return get_proximity_range(get_location(get_ip_address(request)),x_range,y_range)

def get_random_ip():
    """
    return a random website from a list,done for testing purpose in localhost
    :return: a url of a prominent site
    """
    sitelist=['google.com','youtube.com','goal.com','backpack.com']
    choice = int(randint(0,len(sitelist)-1))

    return sitelist[choice];

def get_random_location():
    """
    get location of a randomly selected ip
    :return:an instance of the Location class
    """
    location_dict= get_location(get_random_ip())
    print(location_dict)
    #CAPS
    #if str(location_dict['region_name'])== '':
    #    location_dict['region_name']=location_dict['country_name']
    location_dict['region_name']=location_dict['country']['name']

    location= Location(location_name=str(location_dict['region_name']),location_lat=location_dict['location']['latitude'],location_long=location_dict['location']['longitude'])

    #CAPS
    #location= Location(location_name=str(location_dict['region_name']),location_lat=location_dict['latitude'],location_long=location_dict['longitude'])
    location.save()
    return location

def is_near(latitude,longitude):
    """
    return the valid spreading range(+- 10) of a location based on latitude,longitude
    :param latitude:latitude of the location
    :param longitude:longitude of the location
    :return:a list containing the valid upper and lower bounds of latitude and longitude
    """
    range_loc=[]
    range_loc.append(latitude+10.00)
    range_loc.append(latitude-10.00)
    range_loc.append(longitude+10.00)
    range_loc.append(longitude-10.00)
    return range_loc

#view functions
def index(request):
    """
    loads the initial web page showing the client the basic view of the website
    if the user is logged in then redirects the user to Newsfeed
    :param request: the HTMLRequest
    :return: either the index.html template if the user is not logged in
            or newsfeed if the user is logged in
    """
    context = RequestContext(request)

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse(newsfeed))
    error = {'has_error':False}
    return render_to_response('index.html', {'error':error}, context)


def aboutus(request):
    """
    The about us page of the site. Contains the information about the site creators.
    login is not required
    :param request:the HTMLRequest
    :return:renders the 'aboutus.html' page
    """
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)

    return render_to_response('aboutus.html', {}, context)


@login_required(login_url='/sharecar/')
def updateinfo(request):
    """
    A page containing the update info form
    :param request:the HTMLRequest
    :return: if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the request method is GET,it shows an update form
             else it writes updated info in database and redirects to 'profile.html'
    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    else:
        if request.method=='POST':
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.about_me=request.POST.get('aboutme')
            userprofile.user.email=request.POST.get('email')

            if request.FILES.get('profile_photo'):
                uploaded_file = request.FILES.get('profile_photo')
                #print(uploaded_file.name)
                parts=uploaded_file.name.split(".")
                #print(parts)
                joinstring=""+request.user.username+'_'+'.'+parts[len(parts)-1]
                uploaded_file.name = joinstring
                userprofile.picture= uploaded_file

            userprofile.save()
            return HttpResponseRedirect(reverse('profile',kwargs={'user_id':request.user.id}))
        # Return a rendered response to send to the client.
        # We make use of the shortcut function to make our lives easier.
        # Note that the first parameter is the template we wish to use.
        return render_to_response('updateinfo.html', {}, context)


@login_required(login_url='/sharecar/')
def profile(request,user_id):
    """
    A page showing the profile of the requested user id
    :param request: the HTMLRequest
    :param user_id: the requested user id
    :return: if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
             else shows user profile with his/her info and posts on
    """
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    #username = UserProfile.objects.get(user=request.user)
    else:
        username = UserProfile.objects.get(user=User.objects.get(id=user_id))
        requested_user_prof=UserProfile.objects.get(user=request.user)
        block_possible_1=Block.objects.filter(blocker=username,blocked=requested_user_prof)
        block_possible_2=Block.objects.filter(blocked=username,blocker=requested_user_prof)
        if len(block_possible_1)+len(block_possible_2)>0:
            return  HttpResponseRedirect(reverse('nopermission'))
        posts = Post.objects.filter(post_maker=username)
        today = datetime.now()
        toplabel = today.strftime('%B')

        # Return a rendered response to send to the client.
        # We make use of the shortcut function to make our lives easier.
        # Note that the first parameter is the template we wish to use.

        post_count=Post.objects.filter(post_maker=username).count()

        profilepostlist=[]
        for post in posts:
            profpost=Profileposts()
            profpost.post_info=post
            choice = int(randint(0,1))
            if choice ==1:
                leftPost = '<div class="col-sm-6 padding-right arrow-right wow fadeInLeft" data-wow-duration="1000ms" data-wow-delay="300ms">'
                leftPost = cgi.escape(leftPost,quote=True)
                profpost.alignment = leftPost
            else:
                rightPost = '<div class=\"col-sm-6\"> <br> </div> <div class=\"col-sm-6 padding-left arrow-left wow fadeInRight\" data-wow-duration=\"1000ms\" data-wow-delay=\"300ms\"\>'
                rightPost = cgi.escape(rightPost,quote=True)
                profpost.alignment = rightPost
            profilepostlist.append(profpost)
            #print(profpost.alignment)
        #print(profilepostlist)
        #print(username.about_me)
        #randlist=[int(randint(0,1)) for i in xrange(post_count)]

        #zipped=zip(posts,randlist)
        #print(zipped)
        blocks=[]
        #print(request.user.id ,int(user_id))
        if request.user.id == int(user_id):
            #print("yes")
            blocks=Block.objects.filter(blocker=username)
        #print(blocks)
        #return render_to_response('dragoon - Codeforces.html',{},context)
        return render_to_response('profile.html', {'posts':profilepostlist,'label':toplabel,'userprofile':username,'blocks':blocks}, context)

@login_required(login_url='/sharecar/')
def profile_by_name(request,user_name):
    """
    A page showing the profile of the requested user

    :param request:the HTMLRequest
    :param user_name:the requested user id

    :return:if the user is not logged in,it redirects to the index page
            else if the user is not verified,it redirects to 'verification.html'
            else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
            else shows user profile with his/her info and posts on

    """
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))    #username = UserProfile.objects.get(user=request.user)
    else:
        username = UserProfile.objects.get(user=User.objects.get(username=user_name))
        requested_user_prof=UserProfile.objects.get(user=request.user)
        block_possible_1=Block.objects.filter(blocker=username,blocked=requested_user_prof)
        block_possible_2=Block.objects.filter(blocked=username,blocker=requested_user_prof)
        if len(block_possible_1)+len(block_possible_2)>0:
            return  HttpResponseRedirect(reverse('nopermission'))

        posts = Post.objects.filter(post_maker=username)
        today = datetime.now()
        toplabel = today.strftime('%B')

        # Return a rendered response to send to the client.
        # We make use of the shortcut function to make our lives easier.
        # Note that the first parameter is the template we wish to use.

        post_count=Post.objects.filter(post_maker=username).count()

        profilepostlist=[]
        for post in posts:
            profpost=Profileposts()
            profpost.post_info=post
            choice = int(randint(0,1))
            if choice ==1:
                leftPost = '<div class="col-sm-6 padding-right arrow-right wow fadeInLeft" data-wow-duration="1000ms" data-wow-delay="300ms">'
                leftPost = cgi.escape(leftPost,quote=True)
                profpost.alignment = leftPost
            else:
                rightPost = '<div class=\"col-sm-6\"> <br> </div> <div class=\"col-sm-6 padding-left arrow-left wow fadeInRight\" data-wow-duration=\"1000ms\" data-wow-delay=\"300ms\"\>'
                rightPost = cgi.escape(rightPost,quote=True)
                profpost.alignment = rightPost
            profilepostlist.append(profpost)
         #   print(profpost.alignment)
        #print(profilepostlist)
        #print(username.about_me)
        #randlist=[int(randint(0,1)) for i in xrange(post_count)]

        #zipped=zip(posts,randlist)
        #print(zipped)
        blocks=[]
        #print(request.user.username ,str(user_name))
        if request.user.username == str(user_name):
         #   print("yes")
            blocks=Block.objects.filter(blocker=username)
        #print(blocks)

        return render_to_response('profile.html', {'posts':profilepostlist,'label':toplabel,'userprofile':username,'blocks':blocks}, context)

def about(request):
    """
    The about us page of the site. Contains the information about the site creators.
    login is not required
    :param request:the HTMLRequest
    :return:renders the 'about.html' page
    """

    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!


    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('about.html', {}, context)


def register(request):
    """
    The registration page renderer
    :param request:The HTMLRequest
    :return: if the request method is POST,registers the ser
            else it just shows the registration form
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user_temp = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']

            )
            userprofile=UserProfile(user=user_temp)
            userprofile.user_NID=form.cleaned_data['NID']
            userprofile.save()
        #    print(userprofile.user.username)
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            #print(request.POST.get('next'))
            return redirect('/sharecar/newsfeed/')
        else:
            error = {'has_error':True, 'message':'invalid input'}
            return HttpResponseRedirect('/sharecar/',{'error':error})

    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
        'form': form
    })

    return render_to_response(
        'index.html',
        variables,
    )


def user_login(request):
    """
    User login renderer
    :param request: The HTMLRequest
    :return: if the user is authenticated,redirects him to newsfeed
            else redirects him to this page again
    """
    context = RequestContext(request)
    logout(request)

    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if (request.POST.get('next') == ''):
                    return redirect('/sharecar/newsfeed/')
                return redirect(request.POST.get('next'))
        error = {'has_error':True,'message':'Username Password do not match'}
        return render_to_response('index.html', {'error': error}, context_instance=RequestContext(request))


@login_required(login_url='/sharecar/')
def newsfeed(request):
    """
    The newsfeed renderer
    :param request: The HTMLRequest
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the request method is GET,it loads the newsfeed
             else it posts status and uploads photo(optionally)

    """
    context = RequestContext(request)

    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        posts=Post.objects.all()
        allblocklist=[]
        allblocklist=find_blocks(request)

        if request.POST:

            post_maker=UserProfile.objects.get(user=request.user)
            post_text=request.POST.get('status')
            post_time=datetime.now()
            post=Post(post_maker=post_maker,post_text=post_text,post_time=post_time,post_sharecount=0)
            if request.FILES.get('post_photo'):
                uploaded_file = request.FILES.get('post_photo')
          #      print(uploaded_file.name)
                parts=uploaded_file.name.split(".")
                #print(parts)
                joinstring=""+post_maker.user.username+'_'+str(post_time)+'.'+parts[len(parts)-1]
                uploaded_file.name = joinstring
                post.post_photo = uploaded_file

            post.save()

        return render_to_response('newsfeed.html', {'posts':posts,'place':"Dhaka",'place_lat':123.45,'place_long':123.45}, context)


# Use the login_required() decorator to ensure only those logged in can access the view.

@login_required(login_url='/sharecar/')
def user_logout(request):
    """
    Destroys the session
    :param request: The HTMLRequest
    :return: logs out the user
    """
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/sharecar/')

@login_required(login_url='/sharecar/')
def cars(request):

    """
    Shows the post of a user within the range
    :param request:The HTMLRequest
    :param
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
            else shows the cars owned by the user,or add the car
    """
    context = RequestContext(request)

    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        owner_of_car=UserProfile.objects.get(user=request.user)
        print(owner_of_car.user.username)
        cars=Car.objects.filter(owner=owner_of_car)

        """
        if request.POST:

            post_maker=UserProfile.objects.get(user=request.user)
            post_text=request.POST.get('status')
            post_time=datetime.now()
            post=Post(post_maker=post_maker,post_text=post_text,post_time=post_time,post_sharecount=0)
            if request.FILES.get('post_photo'):
                uploaded_file = request.FILES.get('post_photo')
          #      print(uploaded_file.name)
                parts=uploaded_file.name.split(".")
                #print(parts)
                joinstring=""+post_maker.user.username+'_'+str(post_time)+'.'+parts[len(parts)-1]
                uploaded_file.name = joinstring
                post.post_photo = uploaded_file

            post.save()
        """

        if request.POST:
            car_owner=UserProfile.objects.get(user=request.user)
            car_registration_number=request.POST.get('registration_number')
            car_model=request.POST.get('model')
            car_number_of_seats=request.POST.get('number_of_seats')
            car=Car(owner=car_owner,registration_number=car_registration_number,car_model=car_model,number_of_seats=car_number_of_seats)
            car.save()


        return render_to_response('car.html', {'cars':cars,'place':"Dhaka",'place_lat':123.45,'place_long':123.45}, context)



@login_required(login_url='/sharecar/')
def sharetrip(request):
    """
    Shares the trip of a user
    :param request:The HTMLRequest
    :param
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
            else shares the trip redirects to previous trip page

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    elif request.POST:

        searchLoc = Location.objects.filter(location_name=request.POST.get('source'))
        if searchLoc:
            source_location = searchLoc[0]
        else:
            source_lat,source_long = geocoder.google(request.POST.get('source')).latlng
            new_location = Location(location_name=request.POST.get('source'),location_lat=source_lat,location_long=source_long)
            new_location.save()
            source_location = new_location
        searchLoc = Location.objects.filter(location_name=request.POST.get('destination'))
        if searchLoc:
            destination_location = searchLoc[0]
        else:
            dest_lat, dest_long = geocoder.google(request.POST.get('destination')).latlng
            new_location = Location(location_name=request.POST.get('destination'),location_long=dest_long,location_lat=dest_lat)
            new_location.save()
            destination_location = new_location
        print request.POST.get('date_of_trip')
        print request.POST.get('time_of_trip')
        trip_date = datetime.strptime(request.POST.get('date_of_trip'),'%Y-%m-%d')
        trip_time = datetime.time(datetime.strptime(request.POST.get('time_of_trip'),'%H:%M'))
        trip_date_time = datetime.combine(trip_date,trip_time)

        car_reg=request.POST.get('car')
        trip_car=Car.objects.get(registration_number=car_reg)

        newTripOffer=Trip(source=source_location, destination=destination_location,
                          trip_time=trip_date_time, car_of_trip=trip_car,
                          created_by_id=user_profile.id,
                          remaining_seats=trip_car.number_of_seats
                          )
        newTripOffer.save()

        return HttpResponseRedirect(reverse('sharetrip'))
    else:
        owner_of_car=UserProfile.objects.get(user=request.user)
        print(owner_of_car.user.username)
        cars=Car.objects.filter(owner=owner_of_car)

        return render_to_response('sharetrip.html', {'cars':cars}, context_instance=RequestContext(request))

@login_required(login_url='/sharecar/')
def spread(request,post_id):
    """
    Spreads the post of a user within the range
    :param request:The HTMLRequest
    :param post_id: the post id
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
            else spreads the post and redirects to newsfeed page

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        spreadedpost=Post.objects.get(pk=post_id)
        spreadedpost.post_sharecount+=1
        spreadedpost.save()

        newpost=Post()
        newpost.post_maker=UserProfile.objects.get(user=request.user)
        newpost.post_text=spreadedpost.post_text
        newpost.post_photo=spreadedpost.post_photo
        newpost.post_sharecount=0
        newpost.post_sharedfrom=spreadedpost
        newpost.post_time=datetime.now()

        newpost.save()
        return HttpResponseRedirect(reverse('newsfeed'))


@login_required(login_url='/carpool/')
def previoustrips(request):
    """
    Shows the previous trip of a user
    :param request:The HTMLRequest
    :param
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
            else sshows the previous trips redirects to newsfeed page

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    print(user_profile.user.username)
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        temp_user= UserProfile.objects.get(user=request.user)

        nowtime=datetime.now()

        pretripsshared=TripRequest.objects.filter(user_requested=temp_user ,trip_status="a",requested_time__lt=nowtime)
        pretripsoffered=Trip.objects.filter(created_by=temp_user , trip_status="c" ,trip_time__lt=nowtime)

        return render_to_response('previoustrips.html', {'pretripsshared':pretripsshared,'pretripsoffered':pretripsoffered,'user_profile':user_profile}, context)

@login_required(login_url='/sharecar/')
def post(request,post_id):

    """
    Shows the post of a user within the range
    :param request:The HTMLRequest
    :param post_id: the post id
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else if the requesting user is blocked by the requested user or has blocked requested user,an error page is shown
            else shows the post
    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        post=Post.objects.get(id=post_id)

        username=post.post_maker
        requested_user_prof=UserProfile.objects.get(user=request.user)
        block_possible_1=Block.objects.filter(blocker=username,blocked=requested_user_prof)
        block_possible_2=Block.objects.filter(blocked=username,blocker=requested_user_prof)
        if len(block_possible_1)+len(block_possible_2)>0:
            return  HttpResponseRedirect(reverse('nopermission'))

        return render_to_response('post.html', {'post':post}, context)


@login_required(login_url='/sharecar/')
def block(request,user_id):
    """
    Blocks the requested user id
    :param request: The HTMLRequest
    :param user_id: the desired blocked user id
    :return: blocks the user id
    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        who_blocked=UserProfile.objects.get(user=request.user)
        who_got_blocked=UserProfile.objects.get(user=User.objects.get(id=user_id))
        block_when=datetime.now()
        block= Block(blocker=who_blocked,blocked=who_got_blocked,block_time=block_when)
        block.save()
        return HttpResponseRedirect(reverse('profile',kwargs={'user_id':request.user.id}))

@login_required(login_url='/sharecar/')
def unblock(request,user_id):
    """
    Unblocks the requested user id
    :param request: The HTMLRequest
    :param user_id: the desired blocked user id
    :return: Unblocks the user id

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        who_blocked=UserProfile.objects.get(user=request.user)
        who_got_blocked=UserProfile.objects.get(user=User.objects.get(id=user_id))

        blockrecord= Block.objects.filter(blocker=who_blocked,blocked=who_got_blocked)
        blockrecord.delete()
        return HttpResponseRedirect(reverse('profile',kwargs={'user_id':request.user.id}))

@login_required(login_url='/sharecar/')
def find_blocks(request):
    """
    returns the blocklist of user along with the list of people who blocked the user
    :param request: The HTMLRequest
    :return: A list containing the users the requested user blocked or vice versa
    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        request_user_profile=UserProfile.objects.get(user=request.user)
        #print(request_user_profile.user.username)

        not_block_list=[]
        not_block_list_1=[]
        not_block_list_2=[]

        temp_block_list_1=Block.objects.filter(Q(blocker=request_user_profile)).values_list('blocked',flat=True)
        temp_block_list_2=Block.objects.filter(Q(blocked=request_user_profile)).values_list('blocker',flat=True)
        not_block_list_1.extend(temp_block_list_1)
        not_block_list_2.extend(temp_block_list_2)

        not_block_list=not_block_list_1+not_block_list_2
        return not_block_list

def nopermission(request):
    """
    Shows the no permission paged in case of block
    :param request: The HTMLRequest
    :return:  if the user is not logged in,it redirects to the index page
             else if the user is not verified,it redirects to 'verification.html'
             else show the no permission page with message
    """
       # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    else:

        # Return a rendered response to send to the client.
        # We make use of the shortcut function to make our lives easier.
        # Note that the first parameter is the template we wish to use.
        return render_to_response('nopermission.html', {}, context)



@login_required(login_url='/sharecar/')
def verification(request):
    requesting_user_profile = request.user.userprofile
    if request.method == 'POST':
        verification_form = VerificationForm(request.POST)
        if verification_form.is_valid():
            verification_code_input = verification_form.cleaned_data['verification_code']
            if verification_code_input == requesting_user_profile.verification_code:
                requesting_user_profile.verification_status = 'A'
                requesting_user_profile.save()
                return HttpResponseRedirect(reverse('newsfeed'))
            else:
                error = {'has_error': True,
                         'message': 'The code you entered does not match with the code in your email',
                         'type': 'code does not match'}
                return render(request, 'verification.html', {'form': verification_form,
                                                             'user_profile': requesting_user_profile,
                                                             'error': error})
        else:
            error = {'has_error': True,
                     'message': 'The code you entered is invalid',
                     'type': 'code does not match'}
            return render(request, 'verification.html', {'form': verification_form,
                                                         'user_profile': requesting_user_profile,
                                                         'error': error})
    else:
        verification_form = VerificationForm()
        print verification_form
        print "hello"
        error = {'has_error': False}
        return render(request, 'verification.html', {'form': verification_form,
                                                     'user_profile': requesting_user_profile,
                                                     'error': error})


@login_required(login_url='/sharecar/')
def change_password(request):
    """//////////////////
    Shows the change password form or changes the password based on request method
    :param request: The HTMLRequest
    :return: if the user is not logged in,redirects to index page
            else if the method is GET,just shows the form
            else updates the password if validated
            else again shows the form with error notice
    """
    requesting_user_profile = request.user.userprofile
    if request.method == 'POST':
        change_password_form = PasswordChangeForm(request.POST)

        if change_password_form.is_valid():

            old_password = change_password_form.cleaned_data['password_old']
            password_1 = change_password_form.cleaned_data['password_1']
            password_2 = change_password_form.cleaned_data['password_2']

            if password_1 == password_2:
                if request.user.check_password(old_password):
                    user = request.user
                    user.set_password(password_1)
                    user.save()
                    return HttpResponseRedirect(reverse('updateinfo'))
                else:
                    error = {'has_error': True,
                             'message': 'The passwords you entered is incorrect',
                             'type': 'incorrect password'}
                    return render(request, 'change_password.html', {'form': change_password_form,
                                                                    'user_profile': requesting_user_profile,
                                                                    'error': error})
            else:
                error = {'has_error': True,
                         'message': 'The passwords you entered do not match',
                         'type': 'new passwords do not match'}
                return render(request, 'change_password.html', {'form': change_password_form,
                                                                'user_profile': requesting_user_profile,
                                                                'error': error})
        else:
            error = {'has_error': True,
                     'message': 'The passwords you entered is invalid',
                     'type': 'invalid password'}
            return render(request, 'change_password.html', {'form': change_password_form,
                                                            'user_profile': requesting_user_profile,
                                                            'error': error})
    else:
        change_password_form = PasswordChangeForm()
        error = {'has_error': False}
        return render(request, 'change_password.html', {'form': change_password_form,
                                                        'user_profile': requesting_user_profile,
                                                        'error': error})


@login_required(login_url='/sharecar/')
def requestatrip(request):

    """
    Gives the user an opportunity to request for a trip
    :param request:The HTMLRequest
    :return:  if the user is not logged in,it redirects to the index page
              else if the user is not verified,it redirects to 'verification.html'
              else the user gives input of the request for which search result is shown

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    elif request.POST:
        source_loc_arr= Location.objects.filter(location_name=request.POST.get('source'))
        destination_loc_arr = Location.objects.filter(location_name=request.POST.get('destination'))
        if source_loc_arr and destination_loc_arr:
            source_loc = source_loc_arr[0]
            destination_loc = destination_loc_arr[0]
        else:
            no_trip_found = []
            return render_to_response('requestatrip.html',{'no_trips':no_trip_found},context)
        trip_date = datetime.strptime(request.POST.get('date_of_trip'),'%Y-%m-%d')
        trip_time = datetime.time(datetime.strptime(request.POST.get('time_of_trip'),'%H:%M'))
        trip_date_time = datetime.combine(trip_date,trip_time)
        end_trip_time = trip_date_time + timedelta(hours=1)
        available_trips = Trip.objects.filter(source=source_loc, destination=destination_loc,
                                              trip_time__range=[trip_date_time,end_trip_time],
                                              remaining_seats__gte=request.POST.get('seats')).exclude(created_by=user_profile)
        seat_wanted = request.POST.get('seats')
        if (available_trips):
            return render_to_response('requestatrip.html', {'available_trips':available_trips,
                                                            'seats_wanted':seat_wanted}, context)
        else:
            no_trip_found = []
            return render_to_response('requestatrip.html',{'no_trips':no_trip_found},context)
    else:
        return render_to_response('requestatrip.html',context)


@login_required(login_url='/sharecar')
def tripapply(request,trip_id, seat_count):
    """
    the rider requests to ride in a trip that was shared by someone else
    :param request: request
    :param trip id: that he/she wants to join
    :return: Unblocks the user id

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        trip = Trip.objects.get(id=trip_id)
        trip_request = TripRequest(user_requested=user_profile,
                                   trip_requested= trip,
                                   requested_time=datetime.now(),
                                   seats_demand=seat_count)
        trip_request.save()
        return pendingrequests(request)


@login_required(login_url='/sharecar/')
def pendingrequests(request):

    """
    Gives the user to view both his pending outgoing and incoming requests
    :param request:The HTMLRequest
    :return:  if the user is not logged in,it redirects to the index page
              else if the user is not verified,it redirects to 'verification.html'
              else the user gives input of the request for which search result is shown

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        outgoing_requests_p = TripRequest.objects.filter(user_requested=user_profile, trip_status="p")
        outgoing_requests_a = TripRequest.objects.filter(user_requested=user_profile, trip_status="a")
        outgoing_requests=outgoing_requests_a|outgoing_requests_p
        #print outgoing_requests
        all_trips_created_by_user = Trip.objects.filter(created_by=user_profile,trip_status="p")
        pending_requests_of_others = TripRequest.objects.filter(trip_status="p").exclude(user_requested=user_profile)
        incoming_requests = []
        for trip_reqs in pending_requests_of_others:
            for trips in all_trips_created_by_user:
                if trip_reqs.trip_requested== trips:
                    incoming_requests.append(trip_reqs)
        #incoming_requests = TripRequest.objects.filter(trip_requested=all_trips_created_by_user,trip_status="p")
        return render_to_response('pendingrequests.html',{'incoming':incoming_requests,
                                                          'outgoing':outgoing_requests
                                                          },context)

@login_required(login_url='/sharecar')
def approve(request,trip_request_id,trip_id, seat_count):
    """
    the rider gets approval to ride in a trip that was shared by someone else
    :param request: request
    :param trip id: that he/she wants to join
    :param seat_count: how many seats
    :return: Unblocks the user id

    """
    context = RequestContext(request)
    user_profile = request.user.userprofile
    if user_profile.verification_status == 'p':
        return HttpResponseRedirect(reverse('verification'))
    else:
        trip = Trip.objects.get(id=trip_id)
        trip.remaining_seats=(Decimal)(trip.remaining_seats)-Decimal(seat_count)
        trip.save()

        trip_request=TripRequest.objects.get(id=trip_request_id)
        trip_request.trip_status="a"
        trip_request.save()

        return pendingrequests(request)


