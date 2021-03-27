import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import selenium.common.exceptions as selenium_exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

from InstaFollower.InstaWebElements import InstaWebElements as webElements
from InstaFollower.InstaOptions import InstaOptions as GetUserOption
from InstaFollower.InstaUtils import InstaUtils


class InstaFollower:

    def __init__(self, username: str, password: str, show_browser=True):
        options = webdriver.ChromeOptions()

        self.username = username
        self.password = password

        if not show_browser:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--remote-debugging-port-9222')
        else:
            options.add_argument("start-maximized")

        options.add_argument("lang=en")
        options.add_argument("user-data-dir=selenium")  # save cookies
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        self.browser_wait = WebDriverWait(self.driver, 10)  # for searching elements (can take longer time9

        self.login_user()

    def __del__(self):
        try:
            self.driver.close()
        except selenium_exceptions.WebDriverException:
            pass

    def login_user(self):
        # go to login
        self.driver.get("https://www.instagram.com/accounts/login/?source=auth_switcher")

        try:
            # look if user is already logged in by previous session
            self.browser_wait.until(ec.presence_of_element_located((By.XPATH, webElements.SEARCH_AFTER_LOGIN)))
            print("successfully logged in")
        except selenium_exceptions.TimeoutException:
            print("User not logged in. No cookies from previous session available")
            print("logging in user...")

            time.sleep(1)

            try:
                cookies_banner_accept_btn = self.driver.find_element_by_xpath(webElements.COOKIE_BANNER)
                cookies_banner_accept_btn.click()
            except selenium_exceptions.NoSuchElementException:
                print("cookie banner not found")

            login = self.browser_wait.until(ec.presence_of_element_located((By.NAME, "username")))
            pw = self.browser_wait.until(ec.presence_of_element_located((By.NAME, "password")))

            login.send_keys(self.username)
            pw.send_keys(self.password)

            del self.password

            login_btn = self.driver.find_element_by_xpath(webElements.LOGIN_BTN)
            login_btn.click()

            try:
                self.browser_wait.until(ec.presence_of_element_located((By.XPATH, webElements.SEARCH_AFTER_LOGIN)))
                print("successfully logged in")

                save_info_login_btn = self.browser_wait.until(
                    ec.presence_of_element_located((By.XPATH, webElements.SAVE_INFO_AFTER_LOGIN_BTN)))

                save_info_login_btn.click()
                time.sleep(5)
            except selenium_exceptions.StaleElementReferenceException as e:
                print("login failed")
                raise ValueError("Fix check element after login")

    def get_element_driver_wait(self, type, name):
        return self.browser_wait.until(ec.presence_of_element_located((type, name)))

    def get_followings(self):
        self.__get_users_in_profile(GetUserOption.FOLLOWINGS)

    def get_followers(self, option: GetUserOption = GetUserOption.FOLLOWERS):
        self.__get_users_in_profile(option)

    def get_unfollowers(self):

        old_follower_exists = False

        if not InstaUtils.file_exists(InstaUtils.followers_path):
            print("No followers available. Gettings followers for user ", self.username)

        self.get_followers(GetUserOption.UNFOLLOWERS)

    def get_non_followers(self):
        self.get_followers()
        self.get_followings()

        InstaUtils.get_non_followers()

    def __get_users_in_profile(self, option: GetUserOption):
        # got to user profile
        self.driver.get("https://www.instagram.com/" + self.username)
        time.sleep(3)

        follower_user_button = None
        file_name = None
        index_profile_count = None
        check_for_unfollower = False

        # followers and following button in profile
        ele = self.driver.find_elements_by_xpath("//a[@class='-nal3 ']")

        # index the buttons (followers and followings)
        if option == GetUserOption.FOLLOWERS or option == GetUserOption.UNFOLLOWERS:
            follower_user_button = ele[0]
            file_name = InstaUtils.followers_path
            index_profile_count = 1

            check_for_unfollower = True if option == GetUserOption.UNFOLLOWERS else False
        elif option == GetUserOption.FOLLOWINGS:
            follower_user_button = ele[1]
            file_name = InstaUtils.followings_path
            index_profile_count = 2

        # all elements count (posts, followers, followings)
        profile_counts = self.driver.find_elements_by_xpath("//span[@class='g47SY ']")

        # get count of followers or followings in profile
        follow_count = profile_counts[index_profile_count].text
        follow_count = follow_count.replace(",", "")

        # open the list (followers or followings)
        follower_user_button.click()

        scroll_bar = self.get_element_driver_wait(By.XPATH, "//div[@class='isgrP']")
        scroll_y = 200

        users = None

        print("Clicking button")

        # specify the text file
        print("file name: ", file_name)

        print("follow count: ", follow_count)

        user_count = 0
        same_number_count = 0
        not_refreshing = False
        old_followers = None
        count_old_followers = 0

        if check_for_unfollower:
            if InstaUtils.file_exists(InstaUtils.followers_path):
                old_followers = InstaUtils.get_all_users_file(InstaUtils.followers_path)
                old_followers = set(old_followers)
                count_old_followers = len(old_followers)

                if len(old_followers) == 0:
                    print("In order to get unfollowers, there need to be old followers")
                    print("No old followers found - getting current Followers.")
                    check_for_unfollower = False

                unfollowers_count = follow_count - count_old_followers
                if unfollowers_count > 0:
                    print("Found {} new unfollowers. Searching for unfollowers..."
                          .format(unfollowers_count))
            else:
                check_for_unfollower = False  # no old followers found

        # scroll through list
        while user_count < int(follow_count):
            print("scrolling...")

            if same_number_count == 20:
                self.driver.execute_script("arguments[0].scroll(200, arguments[1])", scroll_bar, 600)
                time.sleep(2)
                same_number_count = 0
                print("Current users: ", len(users))

                if not_refreshing:
                    break
                not_refreshing = True  # for next run -> we see if no users were found (not loading on instagram)
            else:
                self.driver.execute_script("arguments[0].scroll(200, arguments[0].scrollHeight + arguments[1])",
                                           scroll_bar, scroll_y)
                scroll_y += 200
                time.sleep(.1)
            # get users
            users = self.driver.find_elements_by_xpath("//li[@class='wo9IH']")

            # checks for unfollowers in current list (scrolling through)
            if check_for_unfollower:
                current_followers = set([user.text.split("\n")[0] for user in users])
                unfollowers = old_followers - current_followers

                if len(unfollowers) == count_old_followers:
                    print("Found all new unfollowers")
                    self.save_all_users(unfollowers, InstaUtils.unfollowers_path, "Finished getting unfollowers")
                    check_for_unfollower = False

            if len(users) == user_count:
                same_number_count += 1
            else:
                same_number_count = 0

            user_count = len(users)
            print("current count: ", user_count)

        print("Got {} users".format(user_count))

        self.save_all_users(users, file_name, "finished writing into file!")

    @staticmethod
    def save_all_users(users, file_name, success_msg: str):

        if file_name == InstaUtils.followers_path:
            if InstaUtils.file_exists(InstaUtils.followers_path):
                os.rename(InstaUtils.followers_path, InstaUtils.followers_old_path)

        with open(file_name, 'a') as file:
            # scroll down
            print("writing users into file. this can take a while...")
            for user in users:
                username = user.text.split("\n")[0]
                username += '\n'
                file.write(username)

            print(success_msg)
