import json
import datetime
import requests
from pprintpp import pprint
from requests.exceptions import HTTPError
from config2 import *
import time

# disable warnings
requests.packages.urllib3.disable_warnings()


def is_english(s):
    """
    Check if the target sentence based on English or not
    :param s: Input sentence
    :return: Is English or not
    """
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def restructure_user_name(data_name):
    """
    Re-construct user name based on lastname firstname
    :param data_name: Input user name
    :return: User name after re-structured
    """
    if " " in data_name:
        name_list = data_name.split(" ")
        last_name = name_list.pop(-1)
        tmp_list = [last_name] + name_list

        if is_english(data_name):
            data_name = " ".join(tmp_list)
        else:
            data_name = "".join(tmp_list)
    return data_name


def save_user_profile(user_name, user_info_list):
    """
    Save the matched user info
    :param user_name: Original user name
    :param user_info_list: matched user info list
    """
    data_json = {"original_name": user_name, "info_list": user_info_list}

    if len(user_name) == 0:
        print("Error. No user namne.")
        return None

    output_file_name = "./output/" + user_name[0] + ".txt"

    file_writer = open(output_file_name, "a")
    file_writer.write(json.dumps(data_json) + "\n")
    file_writer.close()


def save_empty_profile(user_name):
    """
    Save orginal user name if there is no matched user info
    :param user_name: Original user name
    """
    if len(user_name) == 0:
        print("Error. No user namne.")
        return None

    output_file_name = "./output/" + "no_match.txt"

    file_writer = open(output_file_name, "a")
    file_writer.write("%s\n" % user_name)
    file_writer.close()


def save_error(error_type, error_info):
    """
    Save error type and error message
    :param error_type: Type of error (HTTP, Except, Response)
    :param error_info: Error message
    """
    current_time = datetime.datetime.now()

    error_message = "%s - %s - %s\n" % (current_time.strftime("%Y-%m-%d %H:%M:%S"), error_type, error_info)
    file_writer = open("./log/error.log", "a")
    file_writer.write(error_message)
    file_writer.close()


def is_match(target_name_list, fb_data):
    """
    Check if the target sentence contain user name
    :param target_name_list: Partial user name splitted by space
    :param fb_data: Target sentence
    :return: Matched or not
    """
    for part_name in target_name_list:
        if part_name not in fb_data:
            return False
    return True


def filter_user_info_by_name(target_name_list, user_info_list):
    """
    Filter user info based on user name
    :param target_name_list: Partial user name splitted by space
    :param user_info_list: List of user info
    :return: Matched user info list
    """
    match_list = list()

    for user_info in user_info_list:
        user_info.pop('network', None)
        fb_name = user_info["name"]
        fb_desc = user_info["description"]

        if is_match(target_name_list, fb_name):
            match_list.append(user_info)
        elif is_match(target_name_list, fb_desc):
            match_list.append(user_info)

    return match_list


def send_request_by_name(data_name):
    """
    Send social buzz get user API
    :param data_name: User name
    :return: Request response
    """
    try:
        sb_user_id_url = SB_URL_TEMPLATE.format(data_name, SB_KEY, SB_NETWORK)
        response = requests.get(sb_user_id_url, headers=DEFAULT_HEADER, verify=False)
        return (True, response)
    except HTTPError as http_err:
        print("HTTP error: %s" % str(http_err))
        save_error("HTTP", str(http_err))
        return (False, str(http_err))
    except Exception as e:
        print("Exception Error: %s" % str(e))
        save_error("Except", str(e))
        return (False, str(e))


def is_exceed_limit(response_json):
    """
    Check if the social buzz API exceed the limit
    :param response_json: Request response
    :return: Is exceed the limit or not
    """
    if "meta" in response_json and "http_code" in response_json["meta"] and response_json["meta"]["http_code"] == 403:
        return True
    return False


def write_number_to_file(number):
    file_writer = open(START_LINE_COUNT_FILE, "w")
    file_writer.write(str(number))
    file_writer.close()


def read_number_from_file():
    if os.path.isfile(START_LINE_COUNT_FILE):
        file_reader = open(START_LINE_COUNT_FILE, "r")
        for line in file_reader:
            number = int(line)
        file_reader.close()
        start_line_count = number
    return start_line_count


def get_id_from_name():
    line_count = 0

    # Read file and get START_LINE_COUNT
    START_LINE_COUNT = read_number_from_file()

    # Loop the user name and fetch user info
    file_reader = open(NAME_LIST_FILE, "r")
    for line in file_reader:
        original_user_name = line.rstrip("\n").replace("  ", " ")
        line_count += 1

        # Skip names before start line
        if SKIP_START_FLAG:
            if line_count < START_LINE_COUNT:
                continue

        # Skip names after finish line
        if SKIP_END_FLAG:
            if line_count >= FINISH_LINE_COUNT:
                print("Reach finish line: %d" % line_count)
                break

        # Stop after target window size
        if MAX_GET_COUNT_FLAG:
            if line_count >= START_LINE_COUNT + MAX_GET_LINE_COUNT:
                print("Reach max get count: %s" % line_count)
                break

        # Re-construct user name
        new_name = restructure_user_name(original_user_name)
        print("%03d: %s" % (line_count, original_user_name))
        print(new_name)

        # Get API response
        request_result = send_request_by_name(new_name)

        # Check request exception
        if request_result[0] is False:
            continue

        # Check if Response.status_code != 200
        response = request_result[1]
        if not response:
            print("Response error: %s" % response.status_code)
            pprint(response.json())
            save_error("Response", json.dumps(response.json()))
            continue

        # Change response into json
        response.encoding = 'utf-8'
        user_info_result = response.json()

        # Check if exceed daily limit
        if is_exceed_limit(user_info_result):
            print("Reach Social Buzz limitation: %d" % line_count)
            print(user_info_result["meta"]["message"])
            write_number_to_file(str(line_count))
            time.sleep(15)
            break

        # Filter incorrect user info based on name
        name_list = original_user_name.split(" ")
        try:
            filtered_user_info_list = filter_user_info_by_name(name_list, user_info_result["posts"])
        except Exception as e:
            print(str(e))
            print(user_info_result)
            continue

        # Save filtered user info
        if len(filtered_user_info_list) > 0:
            save_user_profile(original_user_name, filtered_user_info_list)
            for user_info in filtered_user_info_list:
                pprint(user_info)
        else:
            save_empty_profile(original_user_name)

    file_reader.close()


if __name__ == "__main__":
    for SB_KEY in SB_KEY_LIST:
        print("Using key: %s" % SB_KEY)
        get_id_from_name()
