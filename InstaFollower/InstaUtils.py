import os


class InstaUtils:

    followings_path = "../files/followings.txt"
    followers_old_path = "../files/followers_old.txt"
    followers_path = "files/followers.txt"
    non_followers_path = "../files/non_followers.txt"
    unfollowers_path = "files/unfollowers.txt"

    @staticmethod
    def file_exists(filepath):
        return os.path.exists(filepath)

    @staticmethod
    def get_all_users_file(file_name):
        with open(file_name, 'r') as file:
            users = file.readlines()
            return [line.replace("\n", "") for line in users]

    @classmethod
    def get_non_followers(cls):

        followers = cls.get_all_users_file(cls.followers_path)
        followings = cls.get_all_users_file(cls.followings_path)

        followings = set(followings)
        followers = set(followers)

        non_followers = followings - followers

        with open("../files/non_followers.txt", 'a') as file:
            # scroll down
            for non_follower in non_followers:
                file.write(non_follower + "\n")

            print("Non followers saved in : ", file.name)
