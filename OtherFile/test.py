from aip import AipOcr
import yaml
from pprint import pprint, pp


def recognize(image) -> dict:
    """ recognize words in the given image"""
    with open('settings.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    with open(image, 'rb') as f:
        img = f.read()

    APP_ID = config['APP_ID']
    API_KEY = config['API_KEY']
    SECRET_KEY = config['SECRET_KEY']
    FILE_NAME = config['FILE_NAME']

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    res = client.basicGeneral(img)
    # {'words_result': [{'words': '网友说:我之所以幸运,是因有他们保护】“无论'},
    #               {'words': '哪个时代都有这些最可爱的人,为了我们的安定生活'},
    #               {'words': '而守护。同样的年华,陪伴他们的不是手机、电脑和'},
    #               {'words': '游戏,而是雪山、钢枪和坚定的誓言。”#祖国山河'},
    #               {'words': '寸不能丢#,铭记英雄,致敬边防军人!'}],
    # 'log_id': 1363466493026631680,
    # 'words_result_num': 5}
    return res


def neat_text(dct) -> str:
    """ make the dictionary readable """
    words = dct['words_result']
    res = ''
    for line in words:
        res += line['words']
    return res

if __name__ == '__main__':
    data = recognize('crop.jpg')
    result = neat_text(data)
    print(result)
