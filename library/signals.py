from django.db.models.signals import post_save  # signals (various)
from django.contrib.auth.models import User     # sender
from django.dispatch import receiver            # receiver (decorator)
from .models import Profile

# When a user is created, a profile is automatically created.
@receiver(post_save, sender=User) # if User object is saved, function is initiated after decorator
def create_profile(sender, instance, created, **kwargs): # instance is the newly created User object.
    if created:
        Profile.objects.create(user=instance)
        print('KWARGS: ', kwargs)


# After editing the user, the profile is also saved
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
