import requests
import json
import cv2
import os
import cv2
import pandas as pd
from django.conf import settings
from django.shortcuts import render
import urllib
import numpy as np



BASE_API_URL="https://152.70.117.82:8443"

def get_request_json(endpoint, verify_ssl=False):
    """Fetch result of API GET request"""
    response = requests.get(endpoint, verify=verify_ssl)
    if response.status_code == 200:
        output = response.json()
    else:
        output = None
    return output
def put_request_json(payload, verify_ssl=False):
    """Fetch result of API PUT request"""
    try:
        response = requests.put(
            BASE_API_URL + "/ords/racedata/ism/update_out_and_snag",
            data=json.dumps(payload),
            verify=verify_ssl,
            headers={"content-type": "application/json"},
        )
        
        print('PUT response status code:', response.status_code)
        print('PUT response body:', response.text)  # Check response body for clues
        print('payload:', payload)
        
        if response.status_code == 200:
            output = response.json().get("o_message", "No message returned")
        else:
            output = f"Error: {response.status_code}, {response.text}"
    
    except Exception as e:
        print("Error occurred while making PUT request:", e)
        output = None
    
    return output


def get_image(url):
    img = url
    return img


def get_image_with_cap(url_img, caption):
    img = f'{url_img} {caption}'
    return img


def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def get_img_from_video(url, stoptime=4000, video_id=None):
    save_dir = os.path.join(settings.MEDIA_ROOT, 'racingapp')
    unique_filename= f"{video_id}.jpg"
    save_path = os.path.join(save_dir, unique_filename)
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_POS_MSEC, stoptime)
    ret, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if video_id =='patrol':
        cv2.imwrite(save_path, image)
        print(f"Image saved as {save_path}")
    else:
    
        original_height, original_width, _ = image.shape
        
        print('original_height', original_height)
        print('original_width', original_width)
        desired_height = 500  
        desired_width = 980   

        cropped_width = min(desired_width, original_width)

        crop_y = (original_height - desired_height) // 2
        
        crop_y = max(0, crop_y)  

        cropped_image = image[crop_y:crop_y + desired_height, 0:cropped_width]
        
        cv2.imwrite(save_path, cropped_image)
        print(f"Image saved as {save_path}")
        
    return os.path.join(settings.MEDIA_URL, 'racingapp', unique_filename)


def crop_image(url):
    image = url_to_image(url)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    y = 0
    x = 0
    h = 150
    w = 1040
    image = image[y : y + h, x : x + w]
    filename= f"croped_image.jpg"
    save_dir = os.path.join(settings.MEDIA_ROOT, 'racingapp')
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, image)
    print(f'croped image saved to {save_path}')
    
    return os.path.join(settings.MEDIA_URL, 'racingapp',filename)

def color_back(val):
    if val == 0:
        return "color: green; font-weight: bold; font-size: 18px"
    elif val == 1:
        return "color: darkgoldenrod; font-weight: bold; font-size: 18px"
    elif val == 2:
        return "color: indianred; font-weight: bold; font-size: 18px"
    elif val == 3:
        return "color: deeppink; font-weight: bold; font-size: 18px"
    elif val == 4:
        return "color: royalblue; font-weight: bold; font-size: 18px"
    elif val == 5:
        return "color: grey; font-weight: bold; font-size: 18px"
    elif val == 6:
        return "color: deepskyblue; font-weight: bold; font-size: 18px"
    elif val == 7:
        return "color: orange; font-weight: bold; font-size: 18px"
    elif val == 8:
        return "color: purple; font-weight: bold; font-size: 18px" 
    elif val == 9:
        return "color: blue; font-weight: bold; font-size: 18px"
    elif val == 10:
        return "color: black; font-weight: bold; font-size: 18px"
    elif val == 11:
        return "color: orange; font-weight: bold; font-size: 18px"
    elif val == 12:
        return "color: crimson; font-weight: bold; font-size: 18px"
    elif val == 13:
        return "color: royalblue; font-weight: bold; font-size: 18px"
    else:
        return "color: cyan; font-weight: bold; font-size: 18px"



def make_rank_diff(back, rank):
    """If the Back is zero, please make the font of Rank double sized and bold."""
    if back == 0:
        output = rank
    else:
        output = rank
    return output
def nan_checker(x):
    if x is None:
        out = 0
    else:
        out = x
    return out

def vw_race_date_raceno():
    """To get race dates"""
    vw_race_date_raceno_corpus = []
    hasMore = True
    offset = 0
    while hasMore:
        latest_races_endpoint = (
            BASE_API_URL
            + f"/ords/speedpro/vw_race_date_raceno_for_racing_silks/?offset={offset}&limit=10000"
        )
        latest_races = get_request_json(latest_races_endpoint, False)
        vw_race_date_raceno_corpus.extend(latest_races["items"])
        offset += 25
        hasMore = latest_races["hasMore"]
    df = pd.DataFrame(vw_race_date_raceno_corpus)
    return df

def vw_racing_silks(race_date="20220327", raceno=1):
    """To get race silks"""
    query = '{"race_date":' + '"' + race_date + '"' + f',"raceno":{raceno}' + "}"
    latest_races_endpoint = BASE_API_URL + "/ords/racedata/vw_racing_silks/?q=" + query
    latest_races = get_request_json(latest_races_endpoint, False)

    df = pd.DataFrame(latest_races["items"])

    return df

def vw_racing_silks_more_than_one_in_same_square(race_date="20220327", raceno=1):
    """To get vw_racing_silks_more_than_one_in_same_square"""
    query = '{"race_date":' + '"' + race_date + '"' + f',"raceno":{raceno}' + "}"
    latest_races_endpoint = (
        BASE_API_URL
        + "/ords/racedata/vw_racing_silks_more_than_one_in_same_square/?limit=100&q="
        + query
    )
    latest_races = get_request_json(latest_races_endpoint, False)
    output = latest_races["items"]
    print("ouput length in same square endpoints: " + str(len(output)))
    if len(output) != 0:
        output = output[0]
        output = f'There are {output["countex"]} horses mapped in Back {output["postrace_calculated_backs"]}'
        print(output)
    else:
        output = ""
    return output
def vw_outs_hotkey(race_date="20220327", raceno=1):
    """To get video time"""
    query = '{"race_date":' + '"' + race_date + '"' + f',"raceno":{raceno}' + "}"
    latest_races_endpoint = BASE_API_URL + "/ords/speedpro/vw_outs_hotkey/?q=" + query
    latest_races = get_request_json(latest_races_endpoint, False)

    output = latest_races["items"]

    if len(output) != 0:
        output = output[0]
        output = nan_checker(output["horse_time_at_800"]) + nan_checker(
            output["race_offset"]
        )
    else:
        output = 1
    return output

def get_pivot_table_patrol(vw_racing_silks_df, vw_racing_silks_df_custom):
    """To get the pivot table"""
    try:
        vw_racing_silks_df_custom_ = vw_racing_silks_df_custom[
            ["Silk", "Horse", "Outs", "Back"]
        ]
        vw_racing_silks_df_custom_ = vw_racing_silks_df_custom_.dropna()
        vw_racing_silks_df_custom_.reset_index(inplace=True)
        vw_racing_silks_df_custom_["Silk"] = vw_racing_silks_df_custom_[
            ["Silk", "Horse"]
        ].apply(lambda x: get_image_with_cap(x.Silk, x.Horse), axis=1)
        vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_.pivot(
            index="Back", columns="Outs", values="Silk"
        )
        vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_pivot[::-1]
        vw_racing_silks_df_custom_pivot.index.name = "Outs →   Back ↓ "
        total = sum(vw_racing_silks_df_custom_pivot.count())
        out_available = total
        vw_racing_silks_df_custom_pivot.loc[
            f"Total ({total})"
        ] = vw_racing_silks_df_custom_pivot.count()
        vw_racing_silks_df_custom_pivot.fillna("", inplace=True)

        center_course_dict = dict(
            zip(vw_racing_silks_df["center_course_cd"], vw_racing_silks_df["distance"])
        )

        if (
            list(center_course_dict.keys())[0] in ["STTT"]
            and list(center_course_dict.values())[0] != 1000
        ):

            vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_.pivot(
                index="Outs", columns="Back", values="Silk"
            )

            vw_racing_silks_df_custom_pivot.index.name = "Back →   Outs ↓ "
            total = sum(vw_racing_silks_df_custom_pivot.count())
            vw_racing_silks_df_custom_pivot[
                f"Total ({total})"
            ] = vw_racing_silks_df_custom_pivot.count(axis="columns")
            vw_racing_silks_df_custom_pivot.fillna("", inplace=True)
            out_available = total

        if (
            list(center_course_dict.keys())[0] in ["STTT"]
            and list(center_course_dict.values())[0] == 1000
        ):

            vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_.pivot(
                index="Back", columns="Outs", values="Silk"
            )
            vw_racing_silks_df_custom_pivot.sort_index(
                axis=0, inplace=True, ascending=False
            )
            vw_racing_silks_df_custom_pivot.sort_index(
                axis=1, inplace=True, ascending=False
            )
            vw_racing_silks_df_custom_pivot.index.name = "Outs →   Back ↓ "
            total = sum(vw_racing_silks_df_custom_pivot.count())
            vw_racing_silks_df_custom_pivot.loc[
                f"Total ({total})"
            ] = vw_racing_silks_df_custom_pivot.count()
            vw_racing_silks_df_custom_pivot.fillna("", inplace=True)
            out_available = total
    except:
        vw_racing_silks_df_custom_pivot = pd.DataFrame()
        out_available = vw_racing_silks_df_custom["Outs"].notnull().sum()
    return vw_racing_silks_df_custom_pivot, out_available


def get_pivot_table_aerial(vw_racing_silks_df, vw_racing_silks_df_custom):
    """To get the pivot table"""
    try:
        vw_racing_silks_df_custom_ = vw_racing_silks_df_custom[
            ["Silk", "Horse", "Outs", "Back"]
        ]
        vw_racing_silks_df_custom_ = vw_racing_silks_df_custom_.dropna()
        vw_racing_silks_df_custom_.reset_index(inplace=True)
        vw_racing_silks_df_custom_["Silk"] = vw_racing_silks_df_custom_[
            ["Silk", "Horse"]
        ].apply(lambda x: get_image_with_cap(x.Silk, x.Horse), axis=1)
        vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_.pivot(
            index="Outs", columns="Back", values="Silk"
        )
        vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_pivot[::-1]
        vw_racing_silks_df_custom_pivot.sort_index(
            axis=1, inplace=True, ascending=False
        )

        vw_racing_silks_df_custom_pivot.index.name = "Back →   Outs ↓ "
        total = sum(vw_racing_silks_df_custom_pivot.count())
        vw_racing_silks_df_custom_pivot.loc[
            f"Total ({total})"
        ] = vw_racing_silks_df_custom_pivot.count()
        vw_racing_silks_df_custom_pivot.fillna("", inplace=True)

        center_course_dict = dict(
            zip(vw_racing_silks_df["center_course_cd"], vw_racing_silks_df["distance"])
        )

        if (
            list(center_course_dict.keys())[0] in ["STTT"]
            and list(center_course_dict.values())[0] != 1000
        ):

            vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_.pivot(
                index="Back", columns="Outs", values="Silk"
            )

            vw_racing_silks_df_custom_pivot.sort_index(
                axis=0, inplace=True, ascending=False
            )
            vw_racing_silks_df_custom_pivot.sort_index(
                axis=1, inplace=True, ascending=False
            )

            vw_racing_silks_df_custom_pivot.index.name = "Outs →   Back ↓ "
            total = sum(vw_racing_silks_df_custom_pivot.count())
            vw_racing_silks_df_custom_pivot[
                f"Total ({total})"
            ] = vw_racing_silks_df_custom_pivot.count(axis="columns")
            vw_racing_silks_df_custom_pivot.fillna("", inplace=True)

        if (
            list(center_course_dict.keys())[0] in ["STTT"]
            and list(center_course_dict.values())[0] == 1000
        ):

            vw_racing_silks_df_custom_pivot = vw_racing_silks_df_custom_.pivot(
                index="Outs", columns="Back", values="Silk"
            )
            vw_racing_silks_df_custom_pivot.sort_index(
                axis=0, inplace=True, ascending=True
            )
            vw_racing_silks_df_custom_pivot.sort_index(
                axis=1, inplace=True, ascending=False
            )
            vw_racing_silks_df_custom_pivot.index.name = "Back →   Outs ↓ "
            total = sum(vw_racing_silks_df_custom_pivot.count())
            out_available = total
            vw_racing_silks_df_custom_pivot.loc[
                f"Total ({total})"
            ] = vw_racing_silks_df_custom_pivot.count()
            vw_racing_silks_df_custom_pivot.fillna("", inplace=True)

    except:
        vw_racing_silks_df_custom_pivot = pd.DataFrame()
        out_available = vw_racing_silks_df_custom["Outs"].notnull().sum()
    return vw_racing_silks_df_custom_pivot, out_available