
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import json
from pymongo import MongoClient
import random
# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)


def create_plans_by_openai():
    plan_dic = [{
    'plan_name':'海外輕鬆型(T2)',
    'insured_amount_price':[2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 11000000, 12000000, 13000000, 14000000, 15000000]
    },
    {'plan_name':'海外安心型(T2)',
    'insured_amount_price':[2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 11000000, 12000000, 13000000, 14000000, 15000000]
    },
    {'plan_name':'早鳥豪華型(U2)',
    'insured_amount_price':[3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 11000000, 12000000, 13000000, 14000000, 15000000]
    }  
    ]  
    for plan in plan_dic:
        for i in range(len(plan['insured_amount_price'])):
            plan_name = plan['plan_name']
            insured_amount_price = plan['insured_amount_price'][i]
            insured_amount_price_10 = insured_amount_price/10
            days = 10
            insurance_premium_price = random.randint(200, 5000)  # 預估保費
            max_trip_cancel_price = random.choice([10000, 20000, 30000])  # 旅程取消(不含傳染病及檢疫) (最高)
            fix_flight_delay_price = random.choice([2000, 3000, 6000]) # 班機延誤 (定額)
            max_trip_change_price = max_trip_cancel_price/2 # 旅程更改(不含傳染病及檢疫) (最高)
            fix_baggage_delay_price = fix_flight_delay_price # 行李延誤 (定額)
            fix_baggage_damage_price = fix_flight_delay_price # 行李損失 (定額)
            fix_file_damage_price = random.choice([1000, 2000]) # 旅行文件損失 (定額)

            fix_divert_price = random.choice([1000, 2000,3000]) # 改降非原定機場 (定額)
            day_hijack_price = fix_divert_price # 劫機保險 (日額)
            fix_food_poisoning_price = fix_divert_price #食物中毒  (定額)
            fix_cash_lost_price = fix_divert_price # 現金竊盜損失 
            max_credit_card_lost_price = None # 信用卡盜用損失
            fix_room_lost_price = None # 居家竊盜損失

            third_party_price = 1000000 # 第三人責任險
            emergency_assistance_price = 1500000 # 急難救助
            
            final_json = json_format(plan_name, insured_amount_price, insurance_premium_price, 1, days, insured_amount_price_10, 
                insured_amount_price_10, insured_amount_price, max_trip_cancel_price, fix_flight_delay_price,
                max_trip_change_price, fix_baggage_delay_price, fix_baggage_damage_price, fix_file_damage_price, fix_divert_price,
                day_hijack_price, fix_food_poisoning_price, fix_cash_lost_price, max_credit_card_lost_price, fix_room_lost_price,
                third_party_price, emergency_assistance_price)
            
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object"},
            messages=[
                {
                "role": "user",
                "content": f"請使用繁體中文生成一個包含旅行保險相關資訊的 JSON 格式。按照{final_json}結構應該包括：旅行保險（包括意外傷害、海外突發疾病等）、不便險（包括旅程取消、班機延誤等）、補償險（如食物中毒、現金竊盜損失等）。每個保險類別下應列出具體項目的索引、支付類型、價格、名稱、描述（使用繁體中文），並列出需要的文件和其他必要資訊。請保持 key 使用英文，value 使用繁體中文描述。其中description(描述)、necessities(需要的文件)的文字請更換並自由編造"
                }
            ]
            )
            json_string = completion.choices[0].message
            data = json.loads(json_string.content)
            # transform Python dict to string
            formatted_json_string = json.dumps(data, indent=4, ensure_ascii=False)
            uri = os.getenv("MONGODB_URI")
            conn = MongoClient(uri)
            db = conn['flying_high']
            collection = db['insurance_guotai']
            try:
                document = json.loads(formatted_json_string)
                document["create_data"] = datetime.now(timezone.utc)
                document["update_date"] = datetime.now(timezone.utc)
                collection.insert_one(document)
            except Exception as e:
                print(e)
        

def json_format(plan_name, insured_amount_price, insurance_premium_price, person_count, days, max_sudden_illness_price, 
                actual_medical_insurance_price, max_death_disability_price, max_trip_cancel_price, fix_flight_delay_price,
                max_trip_change_price, fix_baggage_delay_price, fix_baggage_damage_price, fix_file_damage_price, fix_divert_price,
                day_hijack_price, fix_food_poisoning_price, fix_cash_lost_price, max_credit_card_lost_price, fix_room_lost_price,
                third_party_price, emergency_assistance_price):
    
    return {
    "plan": [{"plan_name":plan_name}],
    "insured_amount": { "price": insured_amount_price, "name": "投保額度" },
    "insurance_premium": { "price": insurance_premium_price, "name": "保費" },
    "country": "日本",
    "person": "本人",
    "person_count":person_count,
    "days":days,
    "travel_insurance": 
    {
        "name": "旅平險",
        "content": 
        [
            {
                "sudden_illness": {
                    "index": 0,
                    "pay_type":"最高",
                    "price": max_sudden_illness_price,
                    "name": "海外突發疾病(甲型)",
                    "description": "覆蓋突發疾病的急診和診所治療，不包括過去180天內接受過治療的先前病況。",
                    "price_detail":[{"clinic":0.005},{"emergency":0.01}],
                    "necessities":["保險金申請書","保險單或其謄本","醫療診斷書或住院證明","醫療費用收據","受益人的身分證明"]
                },
                "medical_insurance": {
                    "index": 1,
                    "pay_type":"實支實付",
                    "price": actual_medical_insurance_price,
                    "name": "傷害醫療(實支實付)",
                    "description": "因意外傷害事故產生的醫療費用，事故需為突發外來的非疾病引起。",
                    "necessities":["保險金申請書","保險單或其謄本","醫療診斷書或住院證明（如非中英文請檢附中文翻譯, 必要時需提供意外傷害事故證明文件","醫療費用明細或醫療證明文件（或醫療費用收據）","受益人的身分證明"]
                },
                "Death_disability": {
                    "index": 2,
                    "pay_type":"最高",
                    "price": max_death_disability_price,
                    "name": "意外事故身故失能(最高)",
                    "description": "因意外傷害在180天內導致死亡或失能，依損害程度支付保險金。",
                    "necessities":[{"失能":["保險金申請書","保險單或其謄本","失能診斷書","受益人之身分證明"]},
                                {"身故":["保險金申請書","保險單或其謄本","被保險人除戶戶籍謄本","受益人之身分證明"]}],
                    "appendix":["神經障害","視力障害","聽覺障害","缺損及機能障害","咀嚼吞嚥及言語機能障害","胸腹部臟器機能障害","臟器切除","膀胱機能障害","脊柱運動障害","上肢缺損障害","手指缺損障害","上肢機能障害"]
                }
            }
        ]
    },
    "travel_inconvenience_insurance": 
    {
        "name": "不便險",
        "content": 
        [
            {
                "trip_cancel": {
                    "index": 0,
                    "pay_type":"最高",
                    "price": max_trip_cancel_price,
                    "name": "旅程取消(最高)",
                    "count":1,
                    "description": "因親屬死亡或重病、法律義務、交通罷工或家園重大災損導致旅程取消的非退還費用。",
                    "necessities":["理賠申請書","旅行契約或交通工具之購票證明或旅館預約證明或票券購買證明","損失費用單據正本","預繳費用無法獲得退款或以其他非貨幣形式償還之證明文件","事故證明文件:死亡證明書或相驗屍體證明書或醫院或醫師開立之病危通知書"]
                },
                "flight_delay": {
                    "index": 1,
                    "pay_type":"定額",
                    "price": fix_flight_delay_price,
                    "name": "班機延誤(定額型)",
                    "count":2,
                    "description": "因定期班機延誤超過四小時而支付賠償，每滿四小時可再次申請賠償。",
                    "necessities":["理賠申請書","機票及登機證或航空業者出具之搭機證明","航空業者所出具載有班機延誤期間之證明"]
                },
                "trip_change": {
                    "index": 2,
                    "pay_type":"最高",
                    "price": max_trip_change_price,
                    "name": "旅程更改保險(最高)",
                    "count":1,
                    "description": "因罷工、戰爭、自然災害或親屬死亡等事故必須更改旅程計畫，增加的交通和住宿費用。",
                    "necessities":["理賠申請書","費用單據正本","預定行程之相關證明文件"]
                },
                "baggage_delay": {
                    "index": 3,
                    "pay_type":"定額",
                    "price": fix_baggage_delay_price,
                    "name": "行李延誤(定額型)",
                    "count":1,
                    "description": "因航空公司處理失誤導致行李延誤超過六小時的賠償。",
                    "necessities":["理賠申請書","公共交通工具業者所出具行李延誤達六小時以上之文件"]
                },
                "baggage_damage": {
                    "index": 4,
                    "pay_type":"定額",
                    "price": fix_baggage_damage_price,
                    "name": "行李損失(定額型)",
                    "count":2,
                    "description": "覆蓋因盜竊、搶劫或航空公司處理失當導致的行李損失或毀損，需於24小時內報警。",
                    "reminder":"對於被保險人未於保險事故發生後二十四小時內向警方報案並取得報案證明者不負理賠責任",
                    "necessities":["理賠申請書","向警方報案證明或公共交通工具業者所開立之事故與損失證明"]
                },
                "file_damage": {
                    "index": 5,
                    "pay_type":"定額",
                    "price": fix_file_damage_price,
                    "name": "旅行文件損失(定額型)",
                    "count":1,
                    "description": "旅行文件（如護照或簽證）遺失或被盜，申請賠償需提供警方報案證明。",
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
                "pay_type":"定額",
                "price":fix_divert_price,
                "name":"改降非原定機場(定額型)",
                "count":2,
                "description": "因改降至非原定機場而支付的賠償。",
                "necessities":["理賠申請書","航空公司出具之證明文件","登機證明文件"]    
            },
            "hijack":{
                "pay_type":"日額",
                "price":day_hijack_price,
                "name":"劫機保險(日額型)",
                "count":10,
                "description": "旅途中遇到劫機事件，依照日額給付賠償，需航空公司證明。",
                "necessities":["理賠申請書","航空公司出具之證航空公司出具或其他足以證明劫機之證明文件"]   
            },
            "food_poisoning":{
                "pay_type":"定額",
                "price":fix_food_poisoning_price,
                "name":"食物中毒(定額型)",
                "count":2,
                "description": "因食物中毒導致的醫療費用，需有醫師的診斷證明。",
                "necessities":["理賠申請書","被保險人診斷證明書"]      
                
            },
            "cash_lost":{
                "pay_type":"定額",
                "price":fix_cash_lost_price,
                "name":"現金竊盜損失(定額型)",
                "count":2,
                "description": "因竊盜、搶劫等導致現金損失，限申請兩次，需提供警方報案證明。",
                "necessities":["理賠申請書","向當地警察機關報案證明"]   
                },
            "credict_card_lost":{
                "pay_type":"最高",
                "price":max_credit_card_lost_price,
                "name":"信用卡盜用損失(最高)",
                "count":1,
                "hours":36,
                "description": "信用卡遺失或盜竊後36小時內未經授權的交易損失，包括掛失及重置費用，需警方報案。",
                "necessities":["理賠申請書","被保險人身分證明文件","向當地警察機關報案證明（自行遺失者無需檢附","掛失止付之證明","信用卡帳單/發行機構證明（證明遭盜刷金額）及繳費證明"]    
                },
            "room_lost":{
                "pay_type":"定額",
                "price":fix_room_lost_price,
                "name":"居家竊盜損失(定額型)",
                "count":1,
                "description": "海外旅行期間國內住所遭竊，導致損失，需警方報案及住所證明文件。",
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
        "description": "對第三方體傷、死亡或財物損害依法負賠償責任。"
        }
    ]
    },
    "emergency_assistance": {
    "name": "急難救助",
    "content": [
        {
        "price": emergency_assistance_price,
        "name": "緊急救援費用保險",
        "description": "海外發生急難時的救助費用，如未成年子女送回費用和親友探視費用等，需提供相關證明。",
        }
    ],"necessities":[{"未成年子女送回費用":["理賠申請書","被保險人重大傷病證明文件、死亡證明書或事故發生之相關證明文件"]},{"親友前往探視或處理善後所需之費用":["理賠申請書","被保險人重大傷病證明文件、死亡證明書或事故發生之相關證明文件","相關費用證明文件正本"]},\
        {"醫療轉送費用":["理賠申請書","被保險人重大傷病證明文件","轉送費用證明文件正本"]},{"遺體運送費用":["理賠申請書","死亡證明書","運送費用證明文件正本"]},\
            {"搜索救助費用":["理賠申請書","必要時，本公司得要求提出事故發生之相關證明文件","費用單據正本","委託他人救援時，該委託文件","費用單據正本"]}]
    }
}
        
if __name__ == '__main__':
    create_plans_by_openai()
    