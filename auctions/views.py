from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.core.files.base import ContentFile
import requests
from .models import User, Category, AuctionListing, Comment, Bid, Watchlist
from decimal import Decimal

def index(request):
    return render(request, "auctions/index.html",{
        "listings" : AuctionListing.objects.all()
    })

def listing_page(request, list_id):
    listing_page = AuctionListing.objects.get(id = list_id)
    is_in_watchlist = False
    comments = Comment.objects.filter(listing=listing_page)
    comment_texts = [comment.comments for comment in comments]

    if request.user.is_authenticated:
        
        if Watchlist.objects.filter(watchlist=list_id, user=request.user):
            is_in_watchlist = True
        else:
            is_in_watchlist = False
        bid_by = Bid.objects.filter(bid_price=listing_page.current_price).last()
        if bid_by:
            bidder_user = bid_by.bidding_by
        else:
            bidder_user = None

        return render(request, "auctions/listing_page.html", {
            "listing" : listing_page ,
            "is_in_watchlist" : is_in_watchlist,
            "owner_name" : str(listing_page.owner).strip(),
            "user_name" : str(request.user.username).strip(),
            "bid_by" : str(bidder_user).strip(),
            "comments" : comment_texts
            })
    else:
        return render(request, "auctions/listing_page.html", {
            "listing" : listing_page ,
            "is_in_watchlist" : is_in_watchlist,
            "owner_name" : str(listing_page.owner).strip(),
            "user_name" : str(request.user.username).strip(),
            "comments" : comment_texts,
            })



def watchlist(request):
    if request.user.is_authenticated:
        user_watchlist = Watchlist.objects.filter(user=request.user)
        return render(request, "auctions/watchlist.html",{
            "watchlistings" : user_watchlist
        })


def add_watchlist(request, listing_id):
    if request.method == "POST":
        if request.user.is_authenticated:
                watchlist_page = AuctionListing.objects.get(id = listing_id)
                add_to_watchlist = Watchlist(watchlist=watchlist_page, user=request.user)
                add_to_watchlist.save()
                return redirect('listing_page', list_id=listing_id)
        else:
            return render(request, "auctions/login.html")
        
def remove_watchlist(request, listing_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            watchlist_page = AuctionListing.objects.get(id = listing_id)
            get_from_watchlist = Watchlist.objects.get(watchlist=watchlist_page, user=request.user)
            get_from_watchlist.delete()
            return redirect('listing_page', list_id=listing_id)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)    #In Django, registered users are typically saved in a database table called auth_user. This table is created and managed by Django's built-in authentication system and is part of the Django authentication framework.

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    error_url = None
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        current_price = request.POST["current_price"]
        category = Category.objects.get(id = int(request.POST["category"]))
        image_url = request.POST["image"]
        created_at = timezone.now
        owner = request.user
        
        try:
            image_request = requests.get(image_url, stream=True)
            image_request.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_url = "Re-Enter with the correct URL"

        if error_url is not None:
            return render(request, "auctions/create.html", {
                "error_url" : error_url,
                 "categories" : Category.objects.all()
            })
        else:
            listing = AuctionListing(title = title ,
                                    description = description,
                                        category = category,
                                        current_price = current_price, 
                                            created_at = created_at,
                                                owner = owner,
                                                    status = True)
            image_name = image_url.split("/")[-1]
            image_content = ContentFile(image_request.content)
            listing.image.save(image_name, image_content, save=True)
            listing.save()    
            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create.html" ,{
            "categories" : Category.objects.all()
        })
    
def place_bid(request, listing_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            new_price = request.POST["new_price"]
            bid_by = request.user
            bid = Bid(bid_price=new_price, bidding_by=bid_by)
            bid.save()
            auction_listing = AuctionListing.objects.get(id=listing_id)
            if (Decimal(new_price) > auction_listing.current_price):
                auction_listing.current_price = new_price
                auction_listing.save()
                return redirect('listing_page', list_id=listing_id)
            else: 
                listing_page = AuctionListing.objects.get(id = listing_id)
                is_in_watchlist = False
                if request.user.is_authenticated:
                    if Watchlist.objects.filter(watchlist=listing_id, user=request.user):
                        is_in_watchlist = True
                    else:
                        is_in_watchlist = False

                    return render(request, "auctions/listing_page.html", {
                        "listing" : listing_page ,
                        "is_in_watchlist" : is_in_watchlist,
                        "owner_name" : str(listing_page.owner).strip(),
                        "user_name" : str(request.user.username).strip(),
                        "error_msg": "Bid with higher then the current price"
                        })
                else:

                    return render(request, "auctions/listing_page.html", {
                        "listing" : listing_page ,
                        "is_in_watchlist" : is_in_watchlist,
                        "owner_name" : str(listing_page.owner).strip(),
                        "user_name" : str(request.user.username).strip(),
                        "error_msg": "Bid with higher then the current price"
                        })
        else:
            return render(request, "auctions/login.html")
            
def close_listing(request, listing_id):
    if request.method =="POST":
        auction_listing = AuctionListing.objects.get(id=listing_id)

        if (auction_listing.owner == request.user):
            auction_listing.status = False
            auction_listing.save()
            return render(request, "auctions/index.html")

def comment(request,listing_id):
    if request.method =="POST":
        listing = AuctionListing.objects.get(id=listing_id)
        comment = request.POST['comment']
        comment = Comment(commented_by = request.user, comments = comment, listing = listing)
        comment.save()
        return redirect('listing_page', list_id=listing_id)

def categories(request):
    category_name = Category.objects.all()
    # auctions = AuctionListing.objects.filter(category=category_name, person=person_name).order_by('id').reverse()
    return render(request, "auctions/categories.html",{
        "categories" : category_name
    })

def category_view(request,category):  
    auctions = AuctionListing.objects.filter(category=category)
    if auctions:
        return render(request, "auctions/category.html",{
            "listings" : auctions,
            "error_msg": "No entries in this category"
        })