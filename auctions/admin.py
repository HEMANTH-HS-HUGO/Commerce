from django.contrib import admin
from .models import User, AuctionListing, Category, Bid, Comment, Watchlist
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "item_type")

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "category", "current_price","created_at", "image", "owner", "status" )
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ("commented_by", "comments", "listing")

class BidAdmin(admin.ModelAdmin):
    list_display = ("bid_price", "bidding_by")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("watchlist", "user")
    


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
