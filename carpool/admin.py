from django.contrib import admin
from carpool.models import UserProfile,Car,Driver,Location,Trip,TripRequest,Ride
from carpool.models import Post,Block

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Car)
admin.site.register(Driver)
admin.site.register(Location)
admin.site.register(Trip)
admin.site.register(TripRequest)
admin.site.register(Ride)
admin.site.register(Post)
admin.site.register(Block)




