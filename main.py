import sys
import argparse
from InstaFollower.InstaFollower import InstaFollower


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get non and undfollowers")
    parser.add_argument("-u", "-username", dest="username", help="Username to login into instagram", default=None)
    parser.add_argument("-p", "-password", dest="password", help="Password to login into instagram", default=None)

    options = parser.parse_args()

    if options.username is None:
        print("Need username to start Instafollower.")
        sys.exit(1)

    if options.password is None:
        with open("files/login") as f:
            options.password = f.read()

    instaFollower = InstaFollower(options.username, options.password)

    del options.password
    opt = None

    # Show user options
    while opt != "3":
        print("1. Get non followers")
        print("2. Get unfollowers")
        print("3. To exit")

        opt = input("Chose option: ")

        if opt == "1":
            instaFollower.get_non_followers()
        elif opt == "2":
            instaFollower.get_unfollowers()
        elif opt == "3":
            sys.exit()
