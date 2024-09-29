from django.shortcuts import render, redirect
from django.contrib.auth import logout  # Make sure this is imported
from django.contrib import messages
from django.conf import settings
import pandas as pd
import cv2
import re
import json
from datetime import datetime
from .utils import (get_image, 
                    get_img_from_video, 
                    get_image_with_cap,
                    get_pivot_table_patrol,
                    get_pivot_table_aerial,
                    color_back, crop_image, 
                    url_to_image, make_rank_diff,
                    put_request_json, nan_checker,
                    vw_racing_silks, vw_race_date_raceno,
                    vw_outs_hotkey,vw_racing_silks_more_than_one_in_same_square
                    )
def race_selection_view(request):
    name =  request.user 
    vw_race_date_raceno_df=vw_race_date_raceno()
    center_course_cd_list = list(set(vw_race_date_raceno_df["center_course_cd"].tolist()))
    center_course_cd_list.append("All")
    center_course_cd = request.GET.get('center_course_cd', sorted(center_course_cd_list)[0])
    
    if center_course_cd == "All":
        center_course_cd = center_course_cd_list
    else:
        center_course_cd = [center_course_cd]

    vw_race_date_raceno_df = vw_race_date_raceno_df[vw_race_date_raceno_df["center_course_cd"].isin(center_course_cd)]

    distance_list = sorted(set(map(int, vw_race_date_raceno_df["distance"].tolist())))
    distance_list.append("All")
    distance_cd = request.GET.get('distance_cd', distance_list[-1])
    
    if distance_cd == "All":
        distance_cd = distance_list
    else:
        distance_cd = [distance_cd]

    work_completed_flag_list = sorted(set(vw_race_date_raceno_df["work_completed_flag"].tolist()))
    work_completed_flag_list.append("Both")
    work_completed_flag = request.GET.get('work_completed_flag', work_completed_flag_list[-1])
    
    if work_completed_flag == "Both":
        work_completed_flag = work_completed_flag_list
    else:
        work_completed_flag = [work_completed_flag]
   
    vw_race_date_raceno_df["race_date"] = vw_race_date_raceno_df["race_date"].apply(
        lambda x: datetime.fromisoformat(x[:-1]).strftime("%d-%b-%Y")
    )

    date_list = list(dict.fromkeys(vw_race_date_raceno_df["race_date"].tolist()))
    race_date = request.GET.get('race_date', date_list[0])
    
    
    
    race_no =sorted(list(set(vw_race_date_raceno_df["raceno"].tolist())))
    print('all race no',race_no)
    race_no = request.GET.get('race_no', race_no[0])
    print("raceno", race_no)
    print(race_date)
    if request.method == "POST":
        horse = request.POST.get('horse')
        print("horse",horse)
        outs = request.POST.get('outs')
        print("outs",outs)
        snag_number = request.POST.get('snag_number')
        if horse and outs and snag_number:
            status_message = put_request_json({
                "horse": horse,
                "race_date": race_date,
                "outs": str(outs),
                "snag_number": str(snag_number),
            })
            print('success message', status_message)
            vw_racing_silks_df = vw_racing_silks(race_date, race_no)
            
        else:
            status_message = "Missing horse, outs, or snag_number data."

    else:
        horse = None
        outs = None
        status_message= None
        snag_number = None

    vw_racing_silks_df=vw_racing_silks(race_date, race_no)
    # print('latest silk daat', vw_racing_silks_df)
    
    vw_racing_silks_df["url_gif"] = vw_racing_silks_df["ccode"].apply(
        lambda x: f"https://racing.hkjc.com/racing/content/Images/RaceColor/{x}.gif"
    )

    horse_dict = dict(zip(vw_racing_silks_df["horse"].tolist(), vw_racing_silks_df["url_gif"].tolist()))

    vw_racing_silks_df_custom = pd.DataFrame()
    vw_racing_silks_df_custom["Back"] = vw_racing_silks_df["postrace_calculated_backs"]#.apply(color_back)
    vw_racing_silks_df_custom.sort_values("Back", inplace=True)
    vw_racing_silks_df_custom["Silk"] = vw_racing_silks_df["url_gif"].apply(get_image)
    vw_racing_silks_df_custom["Hno"] = vw_racing_silks_df["horseno_in_race"]
    vw_racing_silks_df_custom["Horse"] = vw_racing_silks_df["horse"]
    vw_racing_silks_df_custom["Rank"] = vw_racing_silks_df["rank"]
    vw_racing_silks_df_custom["Draw"] = vw_racing_silks_df["draw"]
    vw_racing_silks_df_custom["Outs"] = vw_racing_silks_df["visually_overrirden_or_missing_outs"]
    vw_racing_silks_df_custom["Snag"] = vw_racing_silks_df["shifted_behind_runners_flag"]
    vw_racing_silks_df_custom = vw_racing_silks_df_custom.fillna("")
    vw_racing_silks_df_custom["Snag"] = vw_racing_silks_df_custom["Snag"].apply(
        lambda x: str(int(float(x))) if x != "" else x
    )

    df_first = vw_racing_silks_df_custom.iloc[:5].reset_index(drop=True)
    df_second = vw_racing_silks_df_custom.iloc[5:].reset_index(drop=True)
    df_combined = pd.concat([df_first.add_suffix('_first'), df_second.add_suffix('_second')], axis=1)
    df_combined['Back_color_first'] = df_combined['Back_first'].apply(color_back)
    df_combined['Back_color_second'] = df_combined['Back_second'].apply(color_back)
    df_combined = df_combined.fillna('')
 
    horse_choices = vw_racing_silks_df_custom["Horse"].tolist()
    horse_data = vw_racing_silks_df_custom.set_index("Horse")[["Outs", "Snag", "Silk"]].to_dict(orient="index")

    initial_horse = horse_choices[0]
    initial_outs = vw_racing_silks_df_custom[vw_racing_silks_df_custom["Horse"] == initial_horse]["Outs"].values[0]
    initial_snag = vw_racing_silks_df_custom[vw_racing_silks_df_custom["Horse"] == initial_horse]["Snag"].values[0]
    
    
    vw_racing_silks_df_custom_pivot, out_available = get_pivot_table_patrol(
                    vw_racing_silks_df, 
                    vw_racing_silks_df_custom
                )

    out_values=list(vw_racing_silks_df_custom_pivot.index)
    column_headers = list(vw_racing_silks_df_custom_pivot.columns)
    # print('column headers', column_headers)
    Total_Runners = int(vw_racing_silks_df_custom.shape[0])
    print('Total runner', Total_Runners)
    Pending_Outs= Total_Runners - out_available
    print('Pending outs', Pending_Outs)


    combined_rows = []
    image_url_regex = r'(https?://[^\s]+\.gif)'  

    for i, (index, row) in enumerate(vw_racing_silks_df_custom_pivot.iterrows()):
        row_values = []
        for value in row:
            if isinstance(value, str) and re.search(image_url_regex, value):
                image_url = re.search(image_url_regex, value).group(0)
                player_name = value.replace(image_url, '').strip()
                row_values.append({'image_url': image_url, 'player_name': player_name})
            else:
                row_values.append({'image_url': None, 'player_name': value})

        row_with_out = {'out_value': out_values[i], 'values': row_values}
        combined_rows.append(row_with_out)
    
    date = datetime.strptime(race_date, "%d-%b-%Y").strftime("%Y%m%d")
    # print('deformting data', date)
    patrol_url = f"https://streaminghkjc-a.akamaihd.net/hdflash/replay-patrol/{date[:4]}/{date}/{str(race_no).zfill(2)}/eng/replay-patrol_{date}_{str(race_no).zfill(2)}_eng_2500kbps.mp4"
    patrol_url_1200 = f"https://streaminghkjc-a.akamaihd.net/hdflash/replay-patrol/{date[:4]}/{date}/{str(race_no).zfill(2)}/eng/replay-patrol_{date}_{str(race_no).zfill(2)}_eng_1200kbps.mp4"
    aerial_url = f"https://streaminghkjc-a.akamaihd.net/hdflash/replay-aerial/{date[:4]}/{date}/{str(race_no).zfill(2)}/eng/replay-aerial_{date}_{str(race_no).zfill(2)}_eng_2500kbps.mp4"
    
    crop_image_url=f"https://racing.hkjc.com/racing/content/Images/RaceResult/{date}R{race_no}_L.jpg"
    print("crop_image_url", crop_image_url)
    crop_image_path= crop_image(crop_image_url)
    print("crop_image_path", crop_image_path)
    # print("patrol_url",patrol_url)
    # print("patrol_url_1200",patrol_url_1200)
    # print("aerial_url",aerial_url)
    
   
    stoptime=vw_outs_hotkey(race_date, race_no)
    print('stoptime dat',stoptime)
  
    selected_view = request.GET.get('view_type', 'Replay_Patrol')  # Default to 'patrol'
    show_video = request.GET.get('show_video', 'off') == 'on'  # Checkbox for showing video
    print(selected_view)

    video_url = patrol_url if selected_view == 'Replay_Patrol' else aerial_url
    print('which videw',video_url)
    patrol_img_path, aerial_img_path = None, None
    media_type= 'video' if show_video else 'image'
    if not show_video:    
        try:
            if selected_view == 'Replay_Patrol':
                print('selected view', selected_view)
                print('video url', video_url)
                print('stop time', stoptime)
                patrol_img_path = get_img_from_video(video_url, stoptime*1000, 'patrol')
                print('patrol path',patrol_img_path)
            else:
                print('selected view', selected_view)
                print('video url', video_url)
                print('stop time', stoptime)
                aerial_img_path = get_img_from_video(video_url, stoptime*1000, 'aerial')
                print('aerial path',aerial_img_path)
        except:
            print("Erro capturing image")
    try:
        context = {
                    'selected_view': selected_view,
                    'media_type': media_type,
                    'video_url': video_url if show_video else None,  
                    'patrol_img_path': patrol_img_path if not show_video and selected_view == 'Replay_Patrol' else None,
                    'aerial_img_path': aerial_img_path if not show_video and selected_view == 'Replay_Aerial' else None,
                    
                    'first_name': name.first_name,  
                    'last_name': name.last_name, 
                    'center_course_cd_list': sorted(center_course_cd_list),
                    'distance_list': distance_list,
                    'work_completed_flag_list': work_completed_flag_list,
                    'race_date_list': list(dict.fromkeys(vw_race_date_raceno_df["race_date"].tolist())),
                    'race_no_list': sorted(list(set(vw_race_date_raceno_df["raceno"].tolist()))),
                    'table_data': df_combined.to_dict(orient='records'),
                    'horse_dict': horse_dict,
                    'selected_race_date': race_date,
                    'selected_race_no': race_no,
                    'horse_choices': horse_choices,
                    'horse_image': horse_dict[initial_horse],
                    'initial_horse': initial_horse,
                    'initial_outs': initial_outs,
                    'initial_snag': initial_snag,
                    'horse_data': horse_data,
                    'horse_img': horse_dict.get(horse, ""),
                    'status_message': status_message,
                    

                    'replay_patrol_url': patrol_url,
                    'replay_aerial_url': aerial_url,
                    
                    'column_headers' :column_headers,
                    
                    'pivot_table': vw_racing_silks_df_custom_pivot.to_dict(orient='records'),
                    'new_pivot_table': combined_rows,
                    'out_values': out_values,
                    'out_available': out_available,
                    
                    'Total_Runners': Total_Runners,
                    'Pending_Outs': Pending_Outs,
                    
                    'crop_image_path':crop_image_path,
                }
        return render(request, 'racingapp/pivot_selection.html', context)
    except Exception as e:
        print(f"Error: {e}")

def logout_view(request):
    print("Logout view accessed")  
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logged out successfully!')
        print("User logged out")  
        return redirect('login')  
    else:
        print("Not a POST request")  
        return redirect('racing')