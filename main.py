import os
import sys

import pygame
import requests


class Word:
    def __init__(self, x, y, width, height, scr):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.text = ''
        self.scr = scr
        self.font = pygame.font.SysFont('arial', 20)

    def update(self, i):
        self.text += i

    def draw(self):
        txt_surface = self.font.render(str(self.text), True, (0, 0, 0))
        pygame.draw.rect(self.scr, 'black', (self.x, self.y, self.width, self.height), 1)
        self.scr.blit(txt_surface, (self.x + 10, self.y))


class Button:
    def __init__(self, x, y, width, height, scr, name):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.text = name
        self.scr = scr
        self.font = pygame.font.SysFont('arial', 15)
        self.buttonRect = pygame.Rect(x, y, self.width, self.height)

    def update(self, pos):
        if self.buttonRect.collidepoint(pos):
            return True
        return False

    def draw(self):
        txt_surface = self.font.render(str(self.text), True, (0, 0, 0))
        pygame.draw.rect(self.scr, 'orange', (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.scr, 'black', (self.x, self.y, self.width, self.height), 1)
        self.scr.blit(txt_surface, (self.x + 25, self.y + 5))


def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_request, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code} ({response.reason})""")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def show_map(ll_spn=None, map_type='map', add_params=None):
    if ll_spn:
        map_request = f'http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}'
    else:
        map_request = f'http://static-maps.yandex.ru/1.x/?l={map_type}'

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print('Ошибка')
        print(map_request)
        sys.exit(0)

    map_file = 'map.png'
    try:
        with open(map_file, 'wb') as file:
            file.write(response.content)
    except IOError as e:
        print(e)
        sys.exit(-1)
    return map_file


def get_address(address):
    toponym = geocode(address)
    if not toponym:
        return False

    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
    return toponym_address


def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return False

    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


def main():
    z = 10
    img = None
    adress = ""

    pygame.init()
    font = pygame.font.Font(None, 20)
    screen = pygame.display.set_mode((800, 650))
    word = Word(150, 600, 350, 30, screen)
    butn = Button(10, 600, 100, 30, screen, 'Искать')
    butn_2 = Button(520, 600, 220, 30, screen, 'Сброс поискового результата')
    metka = ''
    string_rendered = font.render(adress, 1, pygame.Color('black'))
    f_poisk = False
    adress = ""
    f = True
    while f:
        if f_poisk:
            if word.text:
                toponym_to_find = get_coordinates(word.text)
                if toponym_to_find:
                    lat, lng = toponym_to_find
                    x_m, y_m = lat, lng
                    metka = f"&pt={x_m},{y_m}"
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    adress = get_address(word.text)
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
            f_poisk = False
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                f = False
            elif i.type == pygame.KEYDOWN:
                if i.key == pygame.K_PAGEUP and z < 17 and img:
                    z += 1
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
                elif i.key == pygame.K_PAGEDOWN and z > 0 and img:
                    z -= 1
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
                elif i.key == pygame.K_BACKSPACE:
                    word.text = word.text[:-1]
                else:
                    if i.unicode.lower() in 'йцукенгшщзхъфывапролджэячсмитьбю ,.1234567890':
                        word.update(i.unicode)
            elif i.type == pygame.KEYUP:
                if i.key == pygame.K_UP and img:
                    lng += 0.01
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
                elif i.key == pygame.K_DOWN and img:
                    lng -= 0.01
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
                elif i.key == pygame.K_LEFT and img:
                    lat -= 0.01
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
                elif i.key == pygame.K_RIGHT and img:
                    lat += 0.01
                    ll_spn = f"ll={lat},{lng}&z={z}" + metka
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
            elif i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == 1:
                    f_poisk = butn.update(i.pos)
                    toponym_to_find = get_coordinates(word.text)
                    if toponym_to_find:
                        lat, lng = toponym_to_find
                        x_m, y_m = lat, lng
                        metka = f"&pt={x_m},{y_m}"
                        ll_spn = f"ll={lat},{lng}&z={z}" + metka
                        adress = get_address(word.text)
                        m_f = show_map(ll_spn, 'map')
                        img = pygame.image.load(m_f).convert()
                    if butn_2.update(i.pos):
                        metka = ''
                        adress = ''
                        ll_spn = f"ll={lat},{lng}&z={z}" + metka
                        m_f = show_map(ll_spn, 'map')
                        img = pygame.image.load(m_f).convert()

                    string_rendered = font.render(adress, 1, pygame.Color('black'))

        screen.fill('white')
        screen.blit(string_rendered, (0, 500))
        word.draw()
        butn.draw()
        butn_2.draw()
        if img:
            screen.blit(img, (0, 0))
        pygame.display.update()
    if img:
        os.remove(m_f)
    pygame.quit()


if __name__ == "__main__":
    main()
