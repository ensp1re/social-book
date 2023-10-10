from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount

# import Profile
admin.site.register(Profile)


# import Post
admin.site.register(Post)


admin.site.register(LikePost)


admin.site.register(FollowersCount)