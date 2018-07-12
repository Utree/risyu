# import sqlite
import sqlite3
# 全角・半角
import mojimoji
# 正規表現
import re

import os
# dir
DBPATH = os.path.dirname(os.path.abspath(__file__)) + "/sojo_syllabus.sqlite"

# 検索キーワードを整える
def adjust(mozi):
    # スペース消す
    mozi = re.sub('\s', '', mozi)
    # アルファベットを大文字に
    mozi = mozi.upper()
    # 日本語以外を半角に
    mozi = mojimoji.zen_to_han(mozi, kana=False)
    # 英数字以外を全角に
    mozi = mojimoji.han_to_zen(mozi, digit=False, ascii=False)
    return mozi
    
def main(USRNUM):
    # データベース接続
    connection = sqlite3.connect(DBPATH)
    # カーソル生成
    cursor = connection.cursor()
    # sqlを実行
    # ユーザー情報
    cursor.execute('SELECT * FROM user_info WHERE name=?', (USRNUM,))
    usr_data = cursor.fetchone()
    taken_class = usr_data[1].split(',')
    try:
        gotten_class = usr_data[2].split(',')
    except:
        gotten_class = []
    
    # 授業一覧　春学期
    cursor.execute('SELECT * FROM sojo LEFT OUTER JOIN class_type ON detail_kamoku = class_name WHERE detail_jyugyokeitai=?;', ("春",))
    all_class = cursor.fetchall()
    class_choice = all_class
    
    # # 科目分類されていないものをチェックする
    # for i in range(len(class_choice)):
    #     if class_choice[i][35] == None:
    #         print(class_choice[i][0] + class_choice[i][1])
    
    # １年生と２年生対象
    if int(USRNUM[:-4]) >= 17:
        # 対象学年に絞る
        tmp = []
        for i in range(len(class_choice)):
            # １年生
            if USRNUM[:-4] == '18':
                if "１" in class_choice[i][0]:
                    tmp.append(class_choice[i])
            # 2年生
            if USRNUM[:-4] == '17':
                if "１" in class_choice[i][0]:
                    tmp.append(class_choice[i])
                if "２" in class_choice[i][0]:
                    tmp.append(class_choice[i])
        class_choice = tmp
    
        # 履修済科目を消す
        tmp = []
        for i in range(len(class_choice)):
            flag = True
            for j in range(len(gotten_class)):
                if adjust(gotten_class[j]) in adjust(class_choice[i][10]):
                    flag = False
                else:
                    pass
            if flag:
                tmp.append(class_choice[i])
        class_choice = tmp
    
        # 対象科目を消す
        tmp = []
        kamoku = ['導入科目', '第一外国語', '第二外国語', '留学生科目', '実習科目', '研究科目']
    
        if USRNUM[:-4] == '17':
            kamoku.append('基幹科目')
    
        for i in range(len(class_choice)):
            flag = True
            for j in range(len(kamoku)):
                if adjust(kamoku[j]) in adjust(class_choice[i][35]):
                    flag = False
                if adjust("テーマ別研究") in adjust(class_choice[i][10]):
                    flag = False
                if adjust("健康・スポーツ科学実習") in adjust(class_choice[i][10]):
                    flag = False
            if flag:
                tmp.append(class_choice[i])
        class_choice = tmp
    
        # 学籍番号から情職を消す
        if USRNUM[:-4] == "18":
            # 180001-180050 は金曜３限
            if int(USRNUM[-4:]) <= 50:
                for i in range(len(class_choice)):
                    if '70930' in str(class_choice[i][9]):
                        del class_choice[i]
                        break
            # 180051-180525 は木曜２限
            elif int(USRNUM[-4:]) <= 525:
                for i in range(len(class_choice)):
                    if '70374' in str(class_choice[i][9]):
                        del class_choice[i]
                        break
    else:
        print("3回生以上は対象外")
    
    
    
    # 履修登録済み科目を確認
    class_preset = all_class
    tmp = []
    for i in range(len(class_preset)):
        flag = False
        for j in range(len(taken_class)):
            if adjust(str(taken_class[j])) == adjust(str(class_preset[i][9])):
                flag = True
        if flag:
            tmp.append(class_preset[i])
    class_preset = tmp
    
    # プリセット群を作る
    if USRNUM[:-4] == "18":
        # 1回生 -> 英語から情社、情倫をセット
        for i in range(len(class_preset)):
            if "英語１ａ" == class_preset[i][10]:
                # 情報社会論
                if "月4" == class_preset[i][16]:
                    if not "70405" in taken_class:
                        taken_class.append("70405")
                # 情報と倫理
                if "月3" == class_preset[i][16]:
                    if not "70407" in taken_class:
                        taken_class.append("70407")
    
        if int(USRNUM) <=  180250:
            # 情報処理　火曜3限 70409
            if not "70409" in taken_class:
                taken_class.append("70409")
            # コンピュータの物理　金曜1限 70413
            if not "70413" in taken_class:
                taken_class.append("70413")
        elif int(USRNUM) <= 180260:
            # 情報処理　火曜3限 70409
            if not "70409" in taken_class:
                taken_class.append("70409")
            # コンピュータの物理　金曜２限 70414
            if not "70414" in taken_class:
                taken_class.append("70414")
        else:
            # 情報処理　金曜3限　70410
            if not "70410" in taken_class:
                taken_class.append("70410")
            # コンピュータの物理　金曜２限 70414
            if not "70414" in taken_class:
                taken_class.append("70414")
    
    # 上回生
    else:
        flag = True
        for i in range(len(gotten_class)):
            if "ソフトウェア実習" in adjust(gotten_class[i]):
                flag = False
                break
            else:
                for j in range(len(taken_class)):
                    # ソフトウェア実習未習得 火曜４限　70585
                    if "70585" in adjust(taken_class[j]):
                        flag = False
                        break
    
        if flag:
            taken_class.append("70585")
    # 履修登録済み科目を確認
    class_preset = all_class
    tmp = []
    for i in range(len(class_preset)):
        flag = False
        for j in range(len(taken_class)):
            if adjust(str(taken_class[j])) == adjust(str(class_preset[i][9])):
                flag = True
        if flag:
            tmp.append(class_preset[i])
    class_preset = tmp
    
    # 導入科目、外国語科目,実習科目,テーマ別科目,スポーツ科目,基幹科目をセット
    tmp = []
    kamoku = ['導入科目', '第一外国語', '第二外国語', '留学生科目', '実習科目', '研究科目']
    
    if USRNUM[:-4] == '18':
        kamoku.append('基幹科目')
    
    for i in range(len(class_preset)):
        flag = False
        for j in range(len(kamoku)):
            if adjust(kamoku[j]) in adjust(class_preset[i][35]):
                flag = True
            if adjust("テーマ別研究") in adjust(class_preset[i][10]):
                flag = True
            if adjust("健康・スポーツ科学実習") in adjust(class_preset[i][10]):
                flag = True
        if flag:
            tmp.append(class_preset[i])
    class_preset = tmp
    
    # 選択肢から同じ名前と時間割が一致する科目を消す
    tmp = []
    for i in range(len(class_choice)):
        flag = True
        for j in range(len(class_preset)):
            # 名前が一致
            if adjust(class_preset[j][10]) in adjust(class_choice[i][10]):
                flag = False
            # 時間割が一致
            elif adjust(class_preset[j][16]) in adjust(class_choice[i][16]):
                flag = False
            else:
                pass
        if flag:
            tmp.append(class_choice[i])
    class_choice = tmp
    
    
    # メッセージ群をつくる
    # 展開のプログラミング言語をとること
    # 留学生、秋入学、教職、スポーツ科目、基幹科目、TOEFL、は未対応
    # キャリアデザインは金４取れません
    # 保存
    connection.commit()
    # 接続を閉じる
    connection.close()

    return class_preset, class_choice