import pandas as pd
import os, sys
import boto3

# pile_csv_path = sys.argv[1]
# loop_csv_path = sys.argv[2]

# setup the boto3
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

# s3 bucket name
bucket_name = 'pht-data'

piles_key = os.environ['piles-key']
loops_key = os.environ['loops-key']

# method for preventing the overwite of existing output files
def duplicate_files(path):
    filename, extension = os.path.splitext(path)
    cnt = 1

    while os.path.exists(path):
        path = filename + " (" + str(cnt) + ")" +extension
        cnt += 1
    return path

def process_pile_heights():
    print("processing piles...")
    # import pile data
    piles_csv = s3_client.get_object(Bucket=bucket_name, Key=piles_key)
    piles_df = pd.read_csv(piles_csv['Body'], dtype=str)
    piles_df = piles_df.set_axis(['X','Y','Z','R','G','B'], axis=1, inplace=False)
    piles_ind_df=piles_df[piles_df['X'].str.contains('# Object')]
    piles_ind=piles_ind_df.index.to_list()

    # import loop data
    lps_csv = s3_client.get_object(Bucket=bucket_name, Key=loops_key)
    lps_df = pd.read_csv(lps_csv['Body'], dtype=str)
    lps_df = lps_df.set_axis(['X','Y','Z','R','G','B'], axis=1, inplace=False)
    lps_ind_df=lps_df[lps_df['X'].str.contains('# Object')]
    lps_ind=lps_ind_df.index.to_list()

    # collect pile ids in array
    i=0
    pile_ids =[]
    while i < len(piles_ind):
        pi_df_rs = piles_ind_df.reset_index()
        pile_id = pi_df_rs['X'][i].split("/")[1]
        if pile_id.startswith('00'):
            pile_id = pile_id[2:]
        if pile_id.startswith('0'):
            pile_id = pile_id[1:]
        pile_ids.append(int(pile_id))
        i += 1

    # collect loop ids in array
    i=0
    loop_ids =[]
    while i < len(lps_ind):
        lp_df_rs = lps_ind_df.reset_index()
        loop_id = lp_df_rs['X'][i].split("/")[1]
        loop_ids.append(int(loop_id))
        i += 1

    # compare pile ids and loop ids
    if pile_ids != loop_ids:
        print("ERROR: Pile ID Mismatch")
    elif int(len(pile_ids)) != int(len(loop_ids)):
        print("ERROR: Object Mismatch")
    else:
        i=0
        pile_elevs = []
        while i < len(piles_ind):
            if i == len(piles_ind) - 1:
                singl_pile = piles_df[(piles_df.index > piles_ind[i])]
                max_height = singl_pile["Z"].max()
                pile_elevs.append(float(max_height))
            else:
                singl_pile = piles_df[(piles_df.index > piles_ind[i]) & (piles_df.index < piles_ind[i+1])]
                max_height = singl_pile["Z"].max()
                pile_elevs.append(float(max_height))
            i += 1

        i=0
        loop_elevs = []
        while i < len(lps_ind):
            if i == len(lps_ind) -1:
                singl_loop = lps_df[(lps_df.index > lps_ind[i])]
                min_height = singl_loop["Z"].min()
                loop_elevs.append(int(float(min_height)))
            else:
                singl_loop = lps_df[(lps_df.index > lps_ind[i]) & (lps_df.index < lps_ind[i+1])]
                min_height = singl_loop["Z"].min()
                loop_elevs.append(int(float(min_height)))
            i += 1

        df=pd.DataFrame(list(zip(pile_ids, loop_elevs, pile_elevs)), columns=['Pile IDs','Loop_Min_Elevations', 'Pile_Max_Elevations'])
        df2 = pd.DataFrame(df['Pile_Max_Elevations']-df['Loop_Min_Elevations'], columns=['Pile_Heights'])
        df = df.join(df2)
        print("Processing Complete")
        df.to_csv(duplicate_files('./pile_heights.csv'), sep=',', encoding='utf-8', index=False)
        s3_resource.Bucket(bucket_name).upload_file(Filename='./pile_heights.csv', Key='pile_heights.csv', ExtraArgs={
                'ServerSideEncryption': 'AES256'
            })
        print("File Uploaded to S3")

process_pile_heights()