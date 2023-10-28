from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import datetime , date 



class User(AbstractUser):
    pass

class Category(models.Model):
    item_type = models.CharField(max_length=25)
    
    def __str__(self):  
        return f"{self.item_type}"


class AuctionListing(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="auction_images/") 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="selling")
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} {self.current_price}"

class Comment(models.Model):
    commented_by =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="commented_by")
    comments = models.TextField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="commented_on")

    def __str__(self):
        return f"{self.commented_by} {self.comments}"

class Bid(models.Model):
    
    bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    bidding_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    def __str__(self):
        return f"{self.bid_price}"
    
class Watchlist(models.Model):
    watchlist = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlists")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watched_by")  

    def __str__(self):
        return f"{self.user.username}"
    