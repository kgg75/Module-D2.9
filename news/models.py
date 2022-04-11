from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Sum

# a = Post.objects.filter(categoryType='AR').order_by('-rating')[:1]
# for i in a:
# 	i.dateCreation.strftime("%Y-%m-%d")
# 	i.author.authorUser.username
# 	i.rating
# 	i.title
# 	i.preview()
# 	best_ar_id = i.id
# c = Comment.objects.filter(commentPost=best_ar_id)
# for i in c:
# 	i.dateCreation.strftime("%Y-%m-%d")
# 	i.commentUser.username
# 	i.rating
# 	i.text

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    # posts = models.ForeignKey('Post', on_delete=models.CASCADE)

    def update_rating(self):
        # суммарный рейтинг каждой статьи автора умножается на 3;
        # #p_rat = self.post_set.all() * 3
        #p_rat = self.post_set.all().aggregate(postRating=Sum('rating'))
        # Post.objects.filter(author=1).values('rating').aggregate(all('rating'))

        p_rat = Post.objects.filter(author=self.user_id).aggregate(Sum('rating'))
        p_rat = int(list(p_rat.values())[0]) * 3
        print("p_rat", p_rat)

        # суммарный рейтинг всех комментариев автора;
        ac_rat = Comment.objects.filter(user=self.user_id).aggregate(Sum('rating'))
        ac_rat = int(list(ac_rat.values())[0])
        print("ac_rat", ac_rat)

        # суммарный рейтинг всех комментариев к статьям автора.
        cp_rat = 0
        for _ in Post.objects.filter(author=self.user_id):
            cp_rat += int(list(Comment.objects.filter(post=_.id).aggregate(Sum('rating')).values())[0])
        print("cp_rat", cp_rat)
        self.rating = p_rat + ac_rat + cp_rat
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Post(models.Model):
    NEWS_TYPES = [('AR', 'статья'), ('NW', 'новость')]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    news_type = models.CharField(max_length=2, choices=NEWS_TYPES)
    #post_category = models.ForeignKey('PostCategory', on_delete=models.CASCADE)
    post_category = models.ManyToManyField(Category, through='PostCategory')
    text = models.TextField()
    head = models.CharField(max_length=127)
    rating = models.IntegerField(default=0)

    # bestPost = Post.objects.all().order_by('-rating')[0]
    # post.comment_set.all()

    def like(self):
        self.rating += 1

    def dislike(self):
        self.rating -= 1

    def preview(self) -> str:
        return self.text[:124] + '...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1

    def dislike(self):
        self.rating -= 1
