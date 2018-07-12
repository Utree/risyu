import requests, bs4

import re

# sqlite3 setup
import sqlite3

# dir
import os

# databaseのパス
dbpath = os.path.dirname(os.path.abspath(__file__)) + '/syllabus.sqlite'

def auth(id, passwd):
    # データベース接続とカーソル生成
    connection = sqlite3.connect(dbpath)
    # 自動コミットにする場合は下記を指定（コメントアウトを解除のこと）
    # connection.isolation_level = None
    cursor = connection.cursor()
    
    # idとpasswdをセット
    user_info = {
        'IDToken1': id,
        'IDToken2': passwd
    }
    # requestsモジュールのインスタンスを作る
    s = requests.Session()
    # 関大のログインサイトにPOST
    portal = s.post('https://aft.auth.kansai-u.ac.jp/amserver/UI/Login/amserver/UI/Login/index.php', data=user_info)

    # idまたはpasswdが間違っている場合
    if 'Authentication failed.' in portal.text:
        return [False, "Login Failed"]
    # ログイン出来た場合
    else:
        # Beautiful Soupでスクレイピング
        user_name = bs4.BeautifulSoup(portal.text, "html5lib")
        # 名前をスクレイプ
        user_name = user_name.find(id="header")
        user_name = user_name.select("table tbody tr td p")
        user_name = re.findall('/>.*</', str(user_name[0]))
        user_name = re.sub('\u3000', '', user_name[0])
        user_name = str(user_name)[2:]
        user_name = str(user_name)[:-2]

        # 教員のログインを弾く。できてるかどうかはわからん
        # 関大のサイトにPOST
        menu = s.post('https://portal.kansai-u.ac.jp/vespine/Top?REQUEST_NAME=CMD_SHOW_MENU_STUDENT&PAGE_ID=top&dummy=aaaa?REQUEST_NAME=CMD_SHOW_MENU_STUDENT&PAGE_ID=top&dummy=aaaa')
        
        # 学籍番号を取得
        user_ID = re.findall('\"[0-9]{10}\"' , menu.text)
        if user_ID:
            user_name = str(user_ID[0])[5:-1]
        
        # 非表示inputのvalueがstudentの場合は学生だと判断する
        if '<input type="hidden" name="USERKN" value="sTuDeNt">' in menu.text:
            # SELECT
            cursor.execute('SELECT * FROM user_info WHERE name=?', (user_name,))
             
            if cursor.fetchone() == None:
                # 時間割をスクレイプ
                risyu_top = s.post('https://jmrs.kyomu.kansai-u.ac.jp/wrsy/riplstb035', data={'menu_id': 'riplsto240'})
                class_codes_list = ''
                class_codes = re.findall(':[0-9]{5}', risyu_top.text)
                if class_codes:
                    for i in range(len(class_codes)):
                        class_codes_list += str(class_codes[i])[1:] + ', '
                
                # 履修済み科目を取得
                got_class = s.post('https://jmrs.kyomu.kansai-u.ac.jp/wrsy/riplsto260')
                # beautifulsoupで構造解析
                got_class_soup = bs4.BeautifulSoup(got_class.text, "html.parser")
                # table>tr>tdをスクレイプ
                table_list = got_class_soup.find_all("table")[1]
                table_list = table_list.find_all("tr")[1:]
                got_class_list = ''
                for i in range(len(table_list)):
                    td_list = table_list[i].find_all("td")
                    # 修得済みのみを取る
                    if td_list[2].text == '修得済':
                        got_class_list += td_list[0].text[1:] + ', '
                # データをセット
                cursor.execute("INSERT INTO user_info VALUES (?, ?, ?, ?, ?)", (user_name,class_codes_list[:-2],got_class_list[:-2],'',''))
            
            # 保存を実行（忘れると保存されないので注意）
            connection.commit()
            # 接続を閉じる
            connection.close()
            
            return [True, user_name]
        # その他の人にはログインさせない
        else:
            return [False, 'You can not access']
