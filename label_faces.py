import pandas as pd
import os
import cv2
import time

def list_dirs(root):
    """ returns a list of all subdirectories in a directory """
    dirs = []
    for item in os.listdir(root):
        d = os.path.join(root, item)
        if os.path.isdir(d):
            dirs.append(d)

    return dirs


def list_jpegs(dir):
    """ returns a list of all jpegs in a directory """
    jpegs = []
    for item in os.listdir(dir):
        d = os.path.join(dir, item)
        if d.endswith('.jpg'):
            jpegs.append(d)
    
    return jpegs


def get_metadata(dir):
    """ 
    gets metadata txt file, converts to/returns a dict.
    idk why I didn't just write to json to begin with,
    but this is a quick fix :)
    """
    metadata = {}
    txt_file = os.path.join(dir, 'response.txt')
    with open(txt_file, 'r') as f:
        for line in f:
            # remove unnecessary symbols
            line = line.replace(" ","")
            line = line.replace("{","")
            line = line.replace("}","")
            line = line.replace("'","")

            # split key value pairs by commas
            kv_pairs = line.split(',')

            # split keys and values by colons
            for kv_pair in kv_pairs:
                kv = kv_pair.split(':')
                k, v = kv[0], kv[1]

                metadata[k] = v
    
    return metadata


def get_participant_number(performance_path):
    """ Gets participant number out of performance path """
    # segment the filepath
    if '/' in performance_path:
        path_segments = performance_path.split('/')
    elif '\\' in performance_path:
        path_segments = performance_path.split('\\')
    
    # get the first 3 characters of the final item in filepath,
    # which corresponds to the subject number
    participant_number = path_segments[-1][0:3]
    return participant_number


def create_video(root_path, frame_paths, video_name='joke.avi'):
    """ Creates a video out of joke frames (image only) """
    # create path to the video
    video_path = os.path.join(root_path, video_name)
    
    # initialize the video
    video = cv2.VideoWriter(video_path, 0, 1, (480, 640))

    # iterate over the jpegs from the joke
    for frame_path in frame_paths:
        # write to the video
        video.write(cv2.imread(frame_path))
    
    # stop writing
    video.release()

    return video_path


def watch_video(video_path):
    """ Plays a video with no sound """
    # Create a VideoCapture object and read from input file
    cap = cv2.VideoCapture(video_path)
    
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video  file")
    
    # Read until video is completed
    while(cap.isOpened()):        
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
        
            # Display the resulting frame
            cv2.imshow('Frame', frame)
            cv2.setWindowProperty('Frame', cv2.WND_PROP_TOPMOST, 1)
        
            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            # frame rate is 4fps                    
            time.sleep(.25)
        
        # Break the loop
        else: 
            break
    
    # When everything done, release 
    # the video capture object
    cap.release()
    
    # Closes all the frames
    cv2.destroyAllWindows()


if __name__ == "__main__":
    """ Used to label the face videos using video classification """
    # get the current working directory
    root = os.getcwd()

    # init the dataframe
    columns = ['participant', 'condition', 'joke', 'video', 'audio', 'human']
    df = pd.DataFrame([], columns=columns)

    # get the directory with the performances
    performance_dir = os.path.join(root, 'performances')
    performance_paths = list_dirs(performance_dir)

    # iterate over the performances
    for performance_path in performance_paths:
        # get the participant number for the performance
        participant = get_participant_number(performance_path)

        # get the jokes in the performance
        joke_paths = list_dirs(performance_path)

        # iterate over the jokes in the performance
        for joke_path in joke_paths:
            # extract metadata for that joke
            metadata = get_metadata(joke_path)
            joke_name = metadata['joke']
            video_label = metadata['video']
            audio_label = metadata['audio']
            condition = metadata['performance_tag_condition']

            # get the jpegs from the joke
            frame_paths = list_jpegs(joke_path)

            # create video from jpegs
            video_path = create_video(root, frame_paths)

            # watch the video
            input("\nPress enter to watch next video: ")
            watch_video(video_path)

            # get the human rating of joke
            while True:
                human_rating = int(input("\tHow would you rate the response? (-1, 0, 1): "))

                # only break on a valid response
                if human_rating == -1 or human_rating == 0 or human_rating == 1:
                    break

            # the dataframe row to be added
            joke_row = {
                'participant': participant,
                'condition': condition,
                'joke': joke_name,
                'video': video_label,
                'audio': audio_label,
                'human': human_rating
                }
            
            # append this joke's data to the dataframe
            df = df.append(joke_row, ignore_index=True)
    
    # write to csv
    rater_name = input("What is your first name? ").lower()
    file_name = os.path.join(root, rater_name+'.csv')
    df.to_csv(file_name, encoding='utf-8', index=False)
