from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model):
    """Model referring to user profile,based on the top of django User model
    about_me->about me text about the user
    picture->profile picture of the user
    last_location->last location of the user

    """
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    pw=models.CharField(max_length=10, blank=True)
    reward=models.IntegerField(blank=True,null=True)
    address = models.CharField(blank=True, max_length=300)
    about_me = models.CharField(blank=True, max_length=300)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    last_location = models.CharField(blank=True, max_length=300)
    user_NID=models.CharField(blank=True,null=True,max_length=30)
    verification_status_choices = (
        ('a', 'active'),
        ('d', 'deactive'),
        ('o', 'other'),
        ('p', 'pending'),
        ('s', 'suspended')
    )
    verification_status = models.CharField(blank=False, max_length=2, choices=verification_status_choices, default='p')
    verification_code = models.CharField(blank=False, max_length=128, default='123456')

    def __unicode__(self):
        return self.user.username

class Location(models.Model):
    """
    Model referring to the different locations of the users.
    """
    location_name = models.CharField(blank=True, max_length=300)
    location_lat = models.FloatField(blank=True, null=True)
    location_long = models.FloatField(blank=True, null=True)

class Car(models.Model):
    """
    Model referring to the different cars of the users.
    """
    
    owner=models.ForeignKey(UserProfile)    #whose car
    registration_number=models.CharField(blank=True,null=True,max_length=300)   #car registration number
    car_model=models.CharField(blank=True,max_length=300,null=True) #which model
    number_of_seats=models.IntegerField(blank=True,null=True)       #how many seats
    #is the car available
    car_availablity_status_choices = (
        ('a', 'active'),
        ('d', 'deactive'),
        ('o', 'other'),
        ('p', 'pending'),
        ('s', 'suspended')
    )
    car_availablity_status = models.CharField(blank=False, max_length=2, choices=car_availablity_status_choices, default='p')
    
class Driver(models.Model):

    """
    Model referring to the different drivers of the owners.
    """

    driver_name=models.CharField(blank=True,null=True,max_length=50)
    driver_employer=models.ForeignKey(UserProfile)
    driver_address=models.CharField(blank=True,null=True,max_length=300)
    driver_NID=models.CharField(blank=True,null=True,max_length=30)



class Trip(models.Model):
    """
    Model referring to the different trips of the users.
    """
    created_by=models.ForeignKey(UserProfile,related_name='userprofile')
    source=models.ForeignKey(Location,related_name="source")
    destination=models.ForeignKey(Location,related_name="destination")
    driver_of_trip=models.ForeignKey(Driver, null=True)
    trip_time=models.DateTimeField(blank=True)
    car_of_trip=models.ForeignKey(Car)
    trip_status_choices = (
        ('a', 'approved'),
        ('d', 'disapproved'),
        ('o', 'other'),
        ('p', 'pending'),
        ('s', 'suspended'),
        ('c','completed'),
    )
    trip_status = models.CharField(blank=False, max_length=2, choices=trip_status_choices, default='p')

class TripRequest(models.Model):

    """
    Model referring to the different trip requests of the users.
    """

    user_requested=models.ForeignKey(UserProfile)
    trip_requested=models.ForeignKey(Trip)
    trip_status_choices = (
        ('a', 'approved'),
        ('d', 'disapproved'),
        ('o', 'other'),
        ('p', 'pending'),
        ('s', 'suspended')
    )
    requested_time=models.DateTimeField(blank=True)
    trip_status = models.CharField(blank=False, max_length=2, choices=trip_status_choices, default='p')


class Ride(models.Model):
    """
    Model referring to the different rides of the users.
    """

    rider=models.ForeignKey(UserProfile)
    trip=models.ForeignKey(Trip)





#class Log(models.Model):
#    logger = models.ForeignKey(UserProfile)
#    logtext = models.CharField(blank=True, max_length=50)
#    timestamp = models.DateTimeField(blank=True)



class Post(models.Model):
    """
    Model referring to the user posts.
    """
    post_maker = models.ForeignKey(UserProfile)
    post_text = models.CharField(blank=True, max_length=300)
    post_photo = models.ImageField(upload_to='post_images/', blank=True)
    post_location = models.ForeignKey(Location, blank=True, null=True)
    post_time = models.DateTimeField(blank=True, null=True)
    post_sharedfrom = models.ForeignKey('self', blank=True, null=True)
    post_sharecount = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-post_time']



class Block(models.Model):
    """
    Model referring to the blocks
    """
    blocker = models.ForeignKey(UserProfile, related_name='user_who_blocked')
    blocked = models.ForeignKey(UserProfile, related_name='user_who_got_blocked')
    block_time = models.DateTimeField(blank=True)


class Profileposts:
    """
    A helper class for rendering profile posts
    """
    def __init__(self):
        self.post_info = Post()
        self.alignment=""

class Rating(models.Model):

    rated_user=models.ForeignKey(UserProfile,related_name="rated_user")
    rated_by_user=models.ForeignKey(UserProfile,related_name="rated_by_user")
    rating_event_choices = (
        ('R', 'Rating'),
        ('CT', 'Create Trip'),
        ('ST', 'Share Trip'),
        ('P', 'Posting'),

    )
    rating_event = models.CharField(blank=False, max_length=5, choices=rating_event_choices, default='R')
    rating_event_id=models.IntegerField(blank=False,null=True)
    earned_rating=models.IntegerField(blank=False,null=True)
