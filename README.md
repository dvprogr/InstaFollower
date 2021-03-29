# InstaFollower
Tool for getting Instagram: Followers - Non-Followers and Unfollowers

## Info & Current Status

* Currently beta - works fine within a range of 500 - 1500 follower __AND__ followings, but also has some bugs (instagram not loading the follower list at any point - loading issues)
* Open for pull requests - any ideas can be submitted!
* macOS
* Windows

## Definition
* Follwings: Users that you follow
* Followers: Users that follow you

## Goals
* Proper saving of data -> currently with textfiles
    * SQLite is an option
* user interface

## Requirements
Before you start using InstaFollower you need to install the requirements.txt.
- Tested with Python 3.8.6+
- pip install -r requirements.txt or python -m pip install -r requirements.txt
- Install chromedriver (needed to parse all users from profile)

## Tutorial
To start InstaFollower run main.py -u "username" -p "yourpassword"

Alternatively you can type in the password in files/login - so everytime you start the program you need to pass your username as an argument only.

- main.py -u yourUserName


__Login is needed only once - it will safe the cookies for future sessions.__
