import os
import time
import json
import random
from instagrapi import Client
from config import load_config

config = load_config()
my_username = config["username"]
password = config["password"]
delaysec = config.get("delay_seconds", 5)
proxy = config.get("proxy")


cl = Client()


if isinstance(proxy, dict) and proxy.get("host") and proxy.get("port"):
    proxy_str = f"{proxy['host']}:{proxy['port']}"
    proxy_user = proxy.get("username")
    proxy_pass = proxy.get("password")
    if proxy_user and proxy_pass:
        cl.set_proxy(proxy_str, username=proxy_user, password=proxy_pass)
    else:
        cl.set_proxy(proxy_str)


session_file = f"{my_username}_session.json"
if os.path.exists(session_file):
    try:
        cl.load_settings(session_file)
        cl.login(my_username, password)
    except:
        print("Oldingi sessiya buzilgan, qayta login qilinmoqda...")
        cl.login(my_username, password)
        cl.dump_settings(session_file)
else:
    cl.login(my_username, password)
    cl.dump_settings(session_file)


def wait():
    time.sleep(random.uniform(delaysec, delaysec + 5))


def get_user_info(target_username):
    try:
        user = cl.user_info_by_username(target_username)
        return {
            "username": user.username,
            "full_name": user.full_name,
            "biography": user.biography,
            "profile_pic_url": str(user.profile_pic_url),
            "follower_count": user.follower_count,
            "following_count": user.following_count,
            "is_private": user.is_private,
            "is_verified": user.is_verified
        }
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None


def get_user_posts(target_username):
    try:
        user = cl.user_info_by_username(target_username)
        medias = cl.user_medias(user.pk, amount=10)
        post_data = []
        for media in medias:
            post_data.append(get_post_details(media))
            wait()
        return post_data
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []


def get_post_details(media):
    try:
        likes = cl.media_likers(media.id)
        comments = cl.media_comments(media.id)

        location_data = {
            "name": media.location.name if media.location else "Unknown",
            "lat": media.location.lat if media.location else None,
            "lng": media.location.lng if media.location else None,
            "address": media.location.address if media.location else "Unknown"
        }

        post_details = {
            "caption": media.caption_text,
            "created_at": media.taken_at.strftime('%Y-%m-%d %H:%M:%S'),
            "location": location_data,
            "like_count": media.like_count,
            "likes": [u.username for u in likes],
            "comments": []
        }

        for c in comments:
            try:
                created = c.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(c, "created_at") else "Unknown"
                post_details["comments"].append({
                    "user": c.user.username,
                    "text": c.text,
                    "created_at": created,
                    "location": getattr(c.user, "location", "Unknown")
                })
            except Exception as e:
                print(f"Error in comment parsing: {e}")
        return post_details
    except Exception as e:
        print(f"Error in get_post_details: {e}")
        return {}


def get_followers(target_username):
    try:
        user = cl.user_info_by_username(target_username)
        followers = cl.user_followers(user.pk, amount=100)
        return [u.username for u in followers.values()]
    except Exception as e:
        print(f"Error fetching followers: {e}")
        return []


def get_following(target_username):
    try:
        user = cl.user_info_by_username(target_username)
        following = cl.user_following(user.pk, amount=100)
        return [u.username for u in following.values()]
    except Exception as e:
        print(f"Error fetching following: {e}")
        return []


def main():
    target = input("Instagram username kiriting: ").strip()
    filename = f"{target}_data.txt"

    all_output = f"Instagram username: {target}\n"

    print("\n--- USER INFO ---")
    userinfo = get_user_info(target)
    userinfo_str = json.dumps(userinfo, indent=4, ensure_ascii=False)
    print(userinfo_str)
    all_output += "\n--- USER INFO ---\n" + userinfo_str + "\n"

    print("\n--- POSTS ---")
    posts = get_user_posts(target)
    posts_str = json.dumps(posts, indent=4, ensure_ascii=False)
    print(posts_str)
    all_output += "\n--- POSTS ---\n" + posts_str + "\n"

    print("\n--- FOLLOWERS ---")
    followers = get_followers(target)
    followers_str = json.dumps(followers, indent=4, ensure_ascii=False)
    print(followers_str)
    all_output += "\n--- FOLLOWERS ---\n" + followers_str + "\n"

    print("\n--- FOLLOWING ---")
    following = get_following(target)
    following_str = json.dumps(following, indent=4, ensure_ascii=False)
    print(following_str)
    all_output += "\n--- FOLLOWING ---\n" + following_str + "\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(all_output)

    print(f"\n✅ Hamma ma’lumotlar '{filename}' fayliga saqlandi.")

if __name__ == "__main__":
    main()
