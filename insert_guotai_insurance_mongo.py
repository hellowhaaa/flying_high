from configparser import ConfigParser
import os
from pymongo import MongoClient
from datetime import datetime, timezone
# TODO variable --------

def insurance_json():
    plan_index = 0  # 方案
    plan_name = '海外輕鬆型(T2)'
    person = "本人" # 幫誰保保險
    days = 2 # 旅遊天數
    person_count = 1  # 幫幾個人保
    # country = '日本' # 旅遊地點
    country = None # 旅遊地點
    # age = 27
    age = None
    
    
 
    insured_amount_price = 5000000  # 投保額度
    insurance_premium_price = 412  # 預估保費
    
    death_disability_price = 5000000 # 意外事故身故失能
    medical_insurance_price = 200000 # 傷害醫療實支實付型
    sudden_illness_price = 200000 # 海外突發疾病(甲型)
    max_trip_cancel_price = 60000  # 旅程取消(不含傳染病及檢疫)

    flight_delay_price = 3000 # 班機延誤
    max_trip_change_price = 30000 # 旅程更改(不含傳染病及檢疫)
    baggage_delay_price = 3000 # 行李延誤
    baggage_damage_price = 3000 # 行李損失
    file_damage_price = 1000 # 旅行文件損失
   

    divert_price = 3000 # 改降非原定機場
    hijack_price = 3000 # 劫機保險(日額)
    food_poisoning_price = 3000 #食物中毒   
    cash_lost_price = 1000 # 現金竊盜損失 
    credict_card_lost_price = None # 信用卡盜用損失
    room_lost_price = None # 居家竊盜損失
    
    third_party_price = 1000000 # 第三人責任險
    emergency_assistance_price = 1500000 # 急難救助
                        
                        
    
    return_json = {
            "plan": [{"plan_index":plan_index, "plan_name":plan_name}],
            "insured_amount": { "price": insured_amount_price, "name": "投保額度" },
            "insurance_premium": { "price": insurance_premium_price, "name": "保費" },
            "country": country,
            "person":person,
            "person_count":person_count,
            "days":days,
            "age": [{"age":age},{"name":"年齡"}],
            "travel_insurance": {
            "name": "旅平險",
            "content": [
                {
                "sudden_illness": {
                    "price": sudden_illness_price,
                    "name": "海外突發疾病(甲型)",
                    "description": [
                    "一、「海外」：係指臺灣、澎湖、金門、馬祖等由中華民國政府所轄範圍以外之地區。二、「突發疾病」：係指被保險人需即時在醫院或診所診療始能避免損及身體健康之疾病，且在本附約生效前一百八十日以內，未曾接受該疾病之診療者。三、「醫院」：係指依照當地醫療法規定領有開業執照並設有病房收治病人之公、私立及醫療法人醫院。四、「診所」：係指依照當地醫療法規定領有開業執照的診所。五、「住院」：係指被保險人經醫師診斷其突發疾病必須入住醫院，且正式辦理住院手續並確實在醫院接受診療者。但不包含相當於中華民國全民健康保險法第五十一條所稱之日間住院及精神衛生法第三十五條所稱之日間留院。六、「醫師」：係指依照當地政府之法令規定，合法領有醫師執照之執業醫師，且非要保人本人或被保險人本人。"
                    ],
                    "price_detail":[{"clinic":0.005},{"emergency":0.01}],
                    "necessities":["保險金申請書","保險單或其謄本","醫療診斷書或住院證明","醫療費用收據","受益人的身分證明"]
                },
                "medical_insurance": {
                    "price": medical_insurance_price,
                    "name": "傷害醫療實支實付型",
                    "description": [
                    "被保險人於本保險契約有效期間內，因遭受意外傷害事故，致其支出醫療費用時，本公司依照本承保項目之約定，給付保險金。前項所稱意外傷害事故，係指非由疾病引起之外來突發事故。"
                    ],
                    "necessities":["保險金申請書","保險單或其謄本","醫療診斷書或住院證明（如非中英文請檢附中文翻譯, 必要時需提供意外傷害事故證明文件","醫療費用明細或醫療證明文件（或醫療費用收據）","受益人的身分證明"]
                    
                },
                "Death_disability": {
                    "price": death_disability_price,
                    "name": "意外事故身故失能",
                    "description": [
                    "被保險人於本保險契約有效期間內遭受第十七條約定的意外傷害事故，自意外傷害事故發生之日起一百八十日以內致成附表所列失能程度之一者，本公司給付失能保險金，其金額按該表所列之給付比例計算。但超過一百八十日致成失能者，受益人若能證明被保險人之失能與該意外傷害事故具有因果關係者，不在此限。"
                    ],
                    "necessities":[{"失能":["保險金申請書","保險單或其謄本","失能診斷書","受益人之身分證明"]},
                                {"身故":["保險金申請書","保險單或其謄本","被保險人除戶戶籍謄本","受益人之身分證明"]}]
                    "appendix":["神經障害","視力障害","聽覺障害","缺損及機能障害","咀嚼吞嚥及言語機能障害","胸腹部臟器機能障害","臟器切除","膀胱機能障害","脊柱運動障害","上肢缺損障害","手指缺損障害","上肢機能障害"]
                }
                }
            ]
            },
            "travel_inconvenience_insurance": {
            "name": "不便險",
            "content": [
                {
                "trip_cancel": {
                    "max_price": max_trip_cancel_price,
                    "name": "旅程取消(不含傳染病及檢疫)",
                    "count":1,
                    "description": [
                    "被保險人於預定海外旅程開始前七日至海外旅行期間開始前，因下列第一款至第四款事故致其必須取消預定之全部旅程，對於被保險人無法取回之預繳團費、交通、住宿及票券之費用，本公司依本保險契約之約定對被保險人負理賠之責：一、被保險人、配偶或三親等內親屬死亡或病危者。二、被保險人於中華民國境內擔任訴訟之證人。三、被保險人預定搭乘之公共交通工具業者之受僱人罷工，致所預定搭乘之班次取消或延誤達二十四小時，或其預定前往之地點發生暴動、民眾騷擾之情事。四、被保險人在中華民國境內住居所之建築物及置存於其內之動產，因火災、洪水、地震、颱風或其他天災毀損，且損失金額超過新臺幣二十五萬元者。前項住宿費用不包含他人同宿之費用，如有他人同宿時，本公司依人數比例計算保險金，最高以本保險單所載保險金額為限。"
                    ],
                    "necessities":["理賠申請書","旅行契約或交通工具之購票證明或旅館預約證明或票券購買證明","損失費用單據正本","預繳費用無法獲得退款或以其他非貨幣形式償還之證明文件","事故證明文件:死亡證明書或相驗屍體證明書或醫院或醫師開立之病危通知書"]
                },
                "flight_delay": {
                    "price": flight_delay_price,
                    "name": "班機延誤",
                    "count":2,
                    "description": [
                    "被保險人於本保險契約保險期間內，以乘客身分所搭乘之定期航班較預定出發時間延誤四小時以上者，本公司依本保險契約約定之保險金額給付保險金。對於班機延誤之理賠金額，每滿四小時給付金額及每次事故最高給付金額本公司以本保險單所載保險金額給付保險金，保險期間內以給付二次事故為限。班機延誤期間之計算，自預定搭乘班機之預定出發之時起，至實際出發之時或第一班替代班機出發之時止。但被保險人因不可抗力因素致無法搭乘第一班替代班機或替代轉接班機者，則班機延誤期間計算至次一班替代班機出發之時止。因前班班機延誤所致錯過轉接班機之延誤與前班班機延誤視為同一延誤事故。第一項之定期航班因故取消而未安排替代班機，且被保險人於保險期間內自行安排替代班機時，本公司依本保險契約之約定對被保險人負理賠之責。"
                    ],
                    "necessities":["理賠申請書","機票及登機證或航空業者出具之搭機證明","航空業者所出具載有班機延誤期間之證明"]
                },
                "trip_change": {
                    "price": max_trip_change_price,
                    "name": "旅程更改保險",
                    "count":1,
                    "description": [
                    "被保險人於海外旅行期間內，因下列事故致被保險人必須更改其預定旅程因而所增加之交通或住宿費用，本公司依本保險契約之約定對被保險人負理賠之責：一、預定搭乘之公共交通工具業者之受僱人罷工，或預定前往之地點發生之戰爭、暴動、民眾騷擾、天災。二、居住於中華民國境內之被保險人配偶或三親等內親屬死亡。三、本次旅程所使用之護照或旅行文件遺失。四、因搭乘汽車、火車、航空器或輪船等發生交通意外事故。前項所增加之交通或住宿費用，以被保險人原預定之交通及住宿同等級之費用為限，惟應扣除可由旅館業者、交通工具業者、旅行社或其他提供旅行、住宿業者處獲得之退款或非貨幣形式償還之等值金額。"
                    ],
                    "necessities":["理賠申請書","費用單據正本","預定行程之相關證明文件"]
                },
                "baggage_delay": {
                    "price": baggage_delay_price,
                    "name": "行李延誤",
                    "count":1,
                    "description": [
                    "被保險人於海外旅行期間內，其隨行託運並取得託運行李領取單之個人行李因公共交通工具業者之處理失當，致其在抵達目的地六小時後仍未領得時，本公司依本保險契約約定之保險金額給付保險金。"
                    ],
                    "necessities":["理賠申請書","公共交通工具業者所出具行李延誤達六小時以上之文件"]
                },
                "baggage_damage": {
                    "price": baggage_damage_price,
                    "name": "行李損失",
                    "count":2,
                    "description": [
                    "被保險人於海外旅行期間內，因下列事故致其所擁有且置於行李箱、手提箱或類似容器內之個人物品遭受毀損或滅失，本公司依本保險契約約定之保險金額給付保險金，但保險期間內以給二次為限。一、竊盜、強盜與搶奪。二、交由所搭乘之公共交通工具業者託運且領有託運行李領取單之隨行託運行李，因該公共交通工具業者處理失當所致之毀損、滅失或遺失。"
                    ],
                    "reminder":"對於被保險人未於保險事故發生後二十四小時內向警方報案並取得報案證明者不負理賠責任"
                    "necessities":["理賠申請書","向警方報案證明或公共交通工具業者所開立之事故與損失證明"]
                },
                "file_damage": {
                    "price": file_damage_price,
                    "name": "旅行文件損失",
                    "count":1,
                    "description": [
                    "被保險人於海外旅行期間內，因本次旅程使用之旅行文件(護照、簽證及其他作為出入國境或通行之文件)被強盜、搶奪、竊盜或遺失時，本公司依約定之保險金額給付保險金。"
                    ],
                    "necessities":["理賠申請書","向警方報案證明"]
                }
                }
            ]
            },
            "compensation_insurance":{
                "name":"旅行補償險",
                "content":[
                    {
                    "divert":{
                        "price":divert_price,
                        "name":"改降非原定機場",
                        "count":2,
                        "description": [
                    "被保險人於海外旅行期間內，因本次旅程使用之旅行文件(護照、簽證及其他作為出入國境或通行之文件)被強盜、搶奪、竊盜或遺失時，本公司依約定之保險金額給付保險金。"
                    ],
                    "necessities":["理賠申請書","航空公司出具之證明文件","登機證明文件"]    
                    },
                    "hijack":{
                        "price":hijack_price,
                        "name":"劫機保險(日額)",
                        "count":10,
                        "description": [
                    "被保險人於海外旅行期間內，因本次旅程使用之旅行文件(護照、簽證及其他作為出入國境或通行之文件)被強盜、搶奪、竊盜或遺失時，本公司依約定之保險金額給付保險金。"
                    ],
                    "necessities":["理賠申請書","航空公司出具之證航空公司出具或其他足以證明劫機之證明文件"]   
                    },
                    "food_poisoning":{
                        "price":food_poisoning_price,
                        "name":"食物中毒",
                        "count":2,
                        "description": [
                    "被保險人於本保險契約保險期間內因食品中毒，經合格醫師診斷並出具診斷證明書者，本公司依本保險契約約定之保險金額給付保險金，但保險期間內以給付二次為限。"
                    ],
                        "necessities":["理賠申請書","被保險人診斷證明書"]      
                        
                    },
                    "cash_lost":{
                        "price":cash_lost_price,
                        "name":"現金竊盜損失",
                        "count":2,
                        "description": [
                    "被保險人於海外旅行期間內，其隨身攜帶或置存於旅館房間內之現金因遭遇竊盜、強盜與搶奪等事故而致損失，本公司依本保險契約約定之保險金額給付保險金，但保險期間內以給付二次為限。前項所稱現金係指現行通用之紙幣、硬幣、支票、匯票或旅行支票。"
                    ],
                        "necessities":["理賠申請書","向當地警察機關報案證明"]   
                        },
                    "credict_card_lost":{
                        "price":credict_card_lost_price,
                        "name":"信用卡盜用損失",
                        "hours":36,
                        "description": [
                    "被保險人於海外旅行期間內，因其所持有之信用卡遺失或遭受竊盜、搶奪而向該信用卡之發行機構掛失或止付前三十六個小時內，因未經授權而遭盜刷之損失，包括信用卡掛失止付及申請重置之費用，本公司依本保險契約之約定對被保險人負理賠之責。前項之損失及費用應扣除該信用卡之發行機構就該信用卡之遺失或遭受竊盜、搶奪事件依約應承擔之部分。被保險人應於知悉信用卡遭受竊盜、搶奪後立即向當地警察機關報案並取得報案證明。但自行遺失者不在此限。"
                    ],
                        "necessities":["理賠申請書","被保險人身分證明文件","向當地警察機關報案證明（自行遺失者無需檢附","掛失止付之證明","信用卡帳單/發行機構證明（證明遭盜刷金額）及繳費證明"]    
                        },
                    "room_lost":{
                        "price":room_lost_price,
                        "name":"居家竊盜損失",
                        "count":1,
                        "description": [
                    "被保險人於海外旅行期間內，其置存於國內住居所之住宅建築物或其內之動產，因遭遇竊盜事故而致損失，本公司依本保險契約約定之保險金額給付保險金，但保險期間內以給付一次為限。"
                    ],
                        "necessities":["理賠申請書","被保險人實際住居所之相關證明文件","向警察機關報案證明"]      
                        }
  
                    }
                ]
            },

            "third_party": {
            "name": "第三人責任險",
            "content": [
                {
                "price": third_party_price,
                "name": "第三人責任險",
                "description": [
                    "被保險人於本保險契約約定之賠償責任期間內，對於第三人之體傷、死亡或財物受損，依法應負賠償責任，而受賠償請求時，本公司依約對被保險人負理賠責任。"
                ]
                }
            ]
            },
            "emergency_assistance": {
            "name": "急難救助",
            "content": [
                {
                "price": emergency_assistance_price,
                "name": "緊急救援費用保險",
                "description": [
                    "被保險人於海外旅行期間內，在海外地區發生急難事故時，本公司依本保險契約之約定對被保險人負理賠之責。1. 未成年子女送回費用 2.親友前往探視或處理善後所需之費用 3.醫療轉送費用 4.  遺體運送費用 5. 搜索救助費用 "
                ]
                }
            ],"necessities":[{"未成年子女送回費用":["理賠申請書","被保險人重大傷病證明文件、死亡證明書或事故發生之相關證明文件"]},{"親友前往探視或處理善後所需之費用":["理賠申請書","被保險人重大傷病證明文件、死亡證明書或事故發生之相關證明文件","相關費用證明文件正本"]},\
                {"醫療轉送費用":["理賠申請書","被保險人重大傷病證明文件","轉送費用證明文件正本"]},{"遺體運送費用":["理賠申請書","死亡證明書","運送費用證明文件正本"]},\
                    {"搜索救助費用":["理賠申請書","必要時，本公司得要求提出事故發生之相關證明文件","費用單據正本","委託他人救援時，該委託文件","費用單據正本"]}
            },
            "update_date":datetime.now(timezone.utc)
        }
    
    collection = insert_mongodb_atlas()
    collection.insert_one(return_json)

def insert_mongodb_atlas():

    uri = "mongodb+srv://root:HCadEw7bWkMlybDF@cluster0.ddhtgvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    conn = MongoClient(uri)
    # Send a ping to confirm a successful connection
    try:
        conn.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    # Create a MongoClient instance
    db = conn['flying_high']
    # Access a collection (similar to a table in relational databases)
    collection = db['insurance_guotai']

    mongo_dblist = conn.list_database_names()
    if "flying_high" in mongo_dblist:
        print("flying_high database 已存在！")
    else:
        print('flying_high database 不存在')
    
    return collection

insurance_json()