import requests

BITRIX_WEBHOOK = "https://zeus.bitrix24.ru/rest/4582/cx4c28t8i1hiujx1/
response = requests.get(f"{BITRIX_WEBHOOK}crm.lead.list.json")

if response.status_code == 200:
    print("✅ Вебхук работает! Список лидов:")
    print(response.json())
else:
    print("❌ Ошибка! Код ответа:", response.status_code)
    print(response.text)