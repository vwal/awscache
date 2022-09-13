################################################################################
# RELEASE: 9 September 2022 - MIT license
# script version 1.0.0
#
# Copyright 2022 Ville Walveranta
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################

# import required modules
import os
import json
import pytz
import datetime
import dateutil.parser
from time import gmtime
from time import strftime
from pathlib import Path
from simple_term_menu import TerminalMenu

# set AWS CLI cache directory
home = str(Path.home())
cache_dir = home + '/.aws/cli/cache'


def invalidate_session(session_file, invalidate_all=False):
    fqfn = os.path.join(cache_dir, session_file)
    if invalidate_all is False:
        if os.path.isfile(fqfn):
            os.remove(fqfn)
    else:
        for this_session_filename in os.listdir(cache_dir):
            invalidate_session(this_session_filename)


def get_data(session_file):
    fn = os.path.join(cache_dir, session_file)

    if os.path.isfile(fn):
        # open the session file
        f = open(fn, "r")

        # get the session JSON object as a dict
        data = json.load(f)

        # Close file
        f.close()

        return data


def get_credentials(data):
    credentials = {"aws_access_key_id": data["Credentials"]["AccessKeyId"],
                   "aws_secret_access_key": data["Credentials"]["SecretAccessKey"],
                   "aws_session_token": data["Credentials"]["SessionToken"],
                   "assumed_role_user": data["AssumedRoleUser"]["Arn"]}
    return credentials


def printout_envvars(session_file):
    data = get_data(session_file)
    credentials = get_credentials(data)

    print("\n")
    print("export AWS_ACCESS_KEY_ID=\"" + credentials["aws_access_key_id"] + "\"")
    print("export AWS_SECRET_ACCESS_KEY=\"" + credentials["aws_secret_access_key"] + "\"")
    print("export AWS_SESSION_TOKEN=\"" + credentials["aws_session_token"] + "\"")
    print("\n")
    return


def printout_sqlvars(session_file):
    data = get_data(session_file)
    credentials = get_credentials(data)

    print("\n")
    print("AWS_ACCESS_KEY_ID '" + credentials["aws_access_key_id"] + "'")
    print("AWS_SECRET_ACCESS_KEY '" + credentials["aws_secret_access_key"] + "'")
    print("AWS_SESSION_TOKEN '" + credentials["aws_session_token"] + "'")
    print("\n")
    return


def session_action(session_file):
    result_data = get_data(session_file)
    selected_credentials = get_credentials(result_data)
    print("Actions for role session " + selected_credentials["assumed_role_user"])
    action_menu_content = ["[b] Show exports for bash",
                           "[s] Show exports for SQL",
                           "[i] Invalidate this session",
                           "[x] Exit (do nothing)"]
    action_terminal_menu = TerminalMenu(action_menu_content, title="Select the action")
    action_menu_entry_index = action_terminal_menu.show()
    if action_menu_entry_index == 0:
        # bash export
        printout_envvars(session_file)
    elif action_menu_entry_index == 1:
        # sql export
        printout_sqlvars(session_file)
    elif action_menu_entry_index == 2:
        # invalidate this session
        invalidate_session(session_file)
        print("The session has been invalidated.\n")
    else:
        exit()


# iterate the cached AWS role session files;
# prompt for selection
selector = list()
menu_content = list()
iterator = 1
for filename in os.listdir(cache_dir):
    this_data = get_data(filename)

    # get session expiration and assumed role user arn
    exp_time = this_data["Credentials"]["Expiration"]
    role_user_arn = this_data["AssumedRoleUser"]["Arn"]

    exp_time_obj = dateutil.parser.parse(exp_time)
    this_time_obj = pytz.utc.localize(datetime.datetime.now())

    if exp_time_obj < this_time_obj:
        # delete expired session
        invalidate_session(filename)
        continue
    else:
        selector.append(filename)
        # get delta (a positive value since we're here)
        time_delta = exp_time_obj - this_time_obj
        # time remaining as HH:MM
        time_remaining = strftime("%H:%M", gmtime(int(time_delta.total_seconds())))

        session_line_item = "[" + str(iterator) + "]" + " " + role_user_arn + " SESSION REMAINING: " + str(time_remaining)
        menu_content.append(session_line_item)
        iterator += 1

print("")
if len(selector) == 0:
    print("No unexpired cached role sessions found.\n")
else:
    selector.append("DELETE_ALL")
    selector.append("EXIT")
    menu_content.append("[a] Invalidate all cached sessions")
    menu_content.append("[x] Exit (do nothing)")
    terminal_menu = TerminalMenu(menu_content, title="Cached role sessions")
    menu_entry_index = terminal_menu.show()
    if not isinstance(menu_entry_index, (int)):
        # ESC was pressed, so exit
        exit()
    selected_filename = selector[menu_entry_index]
    if selected_filename == "EXIT":
        exit()
    elif selected_filename == "DELETE_ALL":
        # invalidate all cached role sessions
        invalidate_session("", True)
        print("All cached role sessions have been invalidated.\n")
    else:
        session_action(selected_filename)
