from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'posts_made')
    content = models.CharField(max_length=280)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Post by {self.user.username} with id {self.id} on {self.timestamp}'

class Like(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'liked_by')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = 'likes', null=True, blank=True)

    def __str__(self):
        return f'Like by {self.user.username} on post {self.post.id}'

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'followers')
    followers = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'follows', null=True, blank=True)

    def __str__(self):
        return f'User {self.user.username} followed by {self.followers}'