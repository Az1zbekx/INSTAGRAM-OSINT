from instagrapi import Client
from config import username, password

cl  = Client()
cl.login(username, password)

def user_info(target):
    user = cl.user_info_by_username(target)
    followers = cl.users_followers(target_user.pk)
    following = cl.user_info_following(user.pk)
    media = cl.user_media(target_user.pk)

    posts = []
    for media in medias:
        likes = cl.media_likes(media.id)
        comments = cl.media_comments(media.id)

        posts.append({
            "caption" : media.caption_text,
            "like_count" : media.like_count,
            "likes" : [u.username for u in likes],
            "comments" : [
               {"user" : c.user.username, "text" : c.text}
               for c in comments
            ]
        }) 

    return {
        "username" : user.username,
        "full name" : user.full_name,
        "biography" : user.biography,
        "follower_count" : user.follower_count,
        "following_count" : user.following_count,
        "is_private" : user.is_private,
        "followers" : [u.username for u in followers.values()],
        "following" : [u.username for u in following.values()],
        "posts" : posts
    }



target = input("Target : ")
