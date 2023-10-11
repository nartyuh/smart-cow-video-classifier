import os
import random
import shutil

'''
This is based on the assumption that the source data directory rougly has the following structured:

source_folder/
    ├── [cow_id]/
    │   ├── bad/
    │   │   ├── approach/
    │   │   │   ├── some_file.MP4
    │   │   │   └── ...
    │   │   ├── direction/
    │   │   │   ├── some_file.MP4
    │   │   │   └── ...
    │   │   ├── human/
    │   │   │   ├── some_file.MP4
    │   │   │   └── ...
    │   │   ├── run/
    │   │   │   ├── some_file.MP4
    │   │   │   └── ...
    │   │   ├── slip/
    │   │   │   ├── some_file.MP4
    │   │   │   └── ...
    │   │   ├── stop/
    │   │   │   ├── some_file.MP4
    │   │   │   └── ...
    │   │   └── two/
    │   │       ├── some_file.MP4
    │   │       └── ...
    │   └── good/
    │       ├── duplicated passing
    │       │   ├── some_file.MP4
    │       │   └── ...
    │       ├── some_file.MP4
    │       └── ...
    └── ...

It's okay for there to be other folders and files; however, the elements in this structure should be organized in such manner for them to be extracted.
'''

BAD = "bad"
GOOD = "good"
DUPLICATED_PASSING = "duplicated passing"
APPROACH = "approach"
DIRECTION = "direction"
HUMAN = "human"
RUN = "run"
SLIP = "slip"
STOP = "stop"
TWO = "two"
BAD_VID_CATEGORIES = {APPROACH, DIRECTION, HUMAN, RUN, SLIP, STOP, TWO}
MP4 = ".mp4"
TRAIN = "train"
TEST = "test"

def build_local_dataset_storage(source, dst, split):
    cow_dirs = get_cow_dirs(source)
    cow_vids = get_and_group_cow_vids(cow_dirs)

    shuffle_bad_vids(cow_vids)
    shuffle_good_vids(cow_vids)
    dataset = split_data(cow_vids, split)

    [print("There are " + str(len(cow_vids[BAD][cat])) + " bad videos under \"" + cat + "\" category.") for cat in BAD_VID_CATEGORIES]
    print("There are " + str(len(cow_vids[GOOD])) + " good videos.")
    print()
    for key in dataset:
        cow_vids_split = dataset[key]
        [print("There are " + str(len(cow_vids_split[BAD][cat])) + " bad videos under \"" + cat + "\" category.") for cat in BAD_VID_CATEGORIES]
        print("There are " + str(len(cow_vids_split[GOOD])) + " good videos.")
        print()
   
    write(dataset, dst)
    print("Finished building local dataset storage.")

def get_cow_dirs(source: str):
    cow_dirs = []

    for file in os.listdir(source):
        file_path = os.path.join(source, file)
        if os.path.isdir(file_path):
            cow_dirs.append(file_path)

    return cow_dirs

def get_and_group_cow_vids(cow_dirs):
    bad_cow_vid_dirs = []
    good_cow_vid_dirs = []

    for dir in cow_dirs:
        for file in os.listdir(dir):
            file_path = os.path.join(dir, file)
            if os.path.isdir(file_path):
                if file == BAD:
                    bad_cow_vid_dirs.append(file_path)
                elif file == GOOD:
                    good_cow_vid_dirs.append(file_path)

    return {
        BAD: get_bad_cow_vids(bad_cow_vid_dirs),
        GOOD: get_good_cow_vids(good_cow_vid_dirs)
    }

def get_bad_cow_vids(bad_cow_vid_dirs):
    bad_cow_vids = {}

    for dir in bad_cow_vid_dirs:
        for file in os.listdir(dir):
            file_path = os.path.join(dir, file)
            if os.path.isdir(file_path):
                if file in BAD_VID_CATEGORIES:
                    for cat in BAD_VID_CATEGORIES:
                        if file == cat:
                            if not cat in bad_cow_vids:
                                bad_cow_vids[cat] = get_vids(file_path)
                            else:
                                bad_cow_vids[cat].extend(get_vids(file_path))

    return bad_cow_vids

def get_good_cow_vids(good_cow_vid_dirs):
    good_cow_vids = []

    for dir in good_cow_vid_dirs:
        good_cow_vids.extend(get_vids(dir))

    return good_cow_vids

def get_vids(dir):
    vids = []

    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if file == DUPLICATED_PASSING:
            vids.extend(get_vids(file_path))
        else:
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() == MP4:
                vids.append(file_path)

    return vids

def shuffle_bad_vids(cow_vids):
    for cat in BAD_VID_CATEGORIES:
        random.shuffle(cow_vids[BAD][cat])

def shuffle_good_vids(cow_vids):
    random.shuffle(cow_vids[GOOD])

def split_data(cow_vids, split):
    train_bad_cow_vids = {}
    test_bad_cow_vids = {}
    bad_cow_vids = cow_vids[BAD]
    for cat in BAD_VID_CATEGORIES:
        bad_cow_vids_in_cat = bad_cow_vids[cat]
        train_bad_cow_vids[cat] = bad_cow_vids_in_cat[:int(len(bad_cow_vids_in_cat) * split)]
        test_bad_cow_vids[cat] = bad_cow_vids_in_cat[int(len(bad_cow_vids_in_cat) * split):]

    good_cow_vids = cow_vids[GOOD]
    train_good_cow_vids = good_cow_vids[:int(len(good_cow_vids) * split)]
    test_good_cow_vids = good_cow_vids[int(len(good_cow_vids) * split):]

    return {
        TRAIN: {
            BAD: train_bad_cow_vids,
            GOOD: train_good_cow_vids
        },
        TEST: {
            BAD: test_bad_cow_vids,
            GOOD: test_good_cow_vids
        }
    }

def write(dataset, dst):
    trainset = dataset[TRAIN]
    testset = dataset[TEST]

    try:
        for cat in BAD_VID_CATEGORIES:
            train_bad_cat_dir = os.path.join(dst, TRAIN, BAD, cat)
            os.makedirs(train_bad_cat_dir)
            test_bad_cat_dir = os.path.join(dst, TEST, BAD, cat)
            os.makedirs(test_bad_cat_dir)
        train_good_dir = os.path.join(dst, TRAIN, GOOD)
        os.makedirs(train_good_dir)
        test_good_dir = os.path.join(dst, TEST, GOOD)
        os.makedirs(test_good_dir)

        for cat in BAD_VID_CATEGORIES:
            for vid in trainset[BAD][cat]:
                shutil.copy(vid, os.path.join(dst, TRAIN, BAD, cat))
            for vid in testset[BAD][cat]:
                shutil.copy(vid, os.path.join(dst, TEST, BAD, cat))

        for vid in trainset[GOOD]:
            shutil.copy(vid, os.path.join(dst, TRAIN, GOOD))
        for vid in testset[GOOD]:
            shutil.copy(vid, os.path.join(dst, TEST, GOOD))
    except FileExistsError:
        print(
            "It seems like some files your want to write already exist. " + 
            "It is recommend to purge local dataset and re-write anew to avoid inconsistencies."
        )
        is_purge_confirmed = input(
            "Do you want to purge current local dataset and re-write anew?:\n" +
            "Note: if aborted, any files that have already been written will persist in the destination folder.\n" +
            "[y/n]: "
        )
        if is_purge_confirmed == "y":
            print("Deleting " + dst + " and re-writing it anew.")
            shutil.rmtree(dst)
            write(dataset, dst)
        else:
            raise

build_local_dataset_storage(
    input("Source dataset directory: "),
    os.path.join(os.getcwd(), "resources", "data"),
    float(input("Split proportion for train and test data (0.0 - 1.0): "))
)
