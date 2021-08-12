import os
import zipfile


def process_for_train(pm):

    mode = 'train'
    _do_preprocess(pm, mode)


def process_for_test(pm):
    """테스트용 데이터 전처리
    """
    mode = 'test'
    _do_preprocess(pm, mode)


def init_svc(im, rule):
    """추론 서비스 초기화
    """
    meta_path = im.meta_path
    return {"meta_path": meta_path, "rule":rule}


def transform(df, params, batch_id):
    """추론을 위한 데이터 변환
    """

    return df

def _do_preprocess(pm, mode):

    source_path = pm.source_path 
    target_path = pm.target_path 
    
    folders = os.listdir(source_path)
    files = []
    for file in folders:
        if file.find('.zip') > -1:
            files.append(file)

    for f in files:
        fantasy_zip = zipfile.ZipFile(os.path.join(source_path,f))
        fantasy_zip.extractall(target_path)
        fantasy_zip.close() 
   
   
