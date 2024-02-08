import os
import sys

import pygame
import requests


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


def get_coordinates():
    return float(50.643918), float(55.372823)


def main():
    z = 10
    toponym_to_find = get_coordinates()
    lat, lng = toponym_to_find
    ll_spn = f"ll={lat},{lng}&z={z}"
    m_f = show_map(ll_spn, 'map')
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    img = pygame.image.load(m_f).convert()
    f = True
    while f:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                f = False
            elif i.type == pygame.KEYDOWN:
                if i.key == pygame.K_PAGEUP and z < 17:
                    z += 1
                    ll_spn = f"ll={lat},{lng}&z={z}"
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
                elif i.key == pygame.K_PAGEDOWN and z > 0:
                    z -= 1
                    ll_spn = f"ll={lat},{lng}&z={z}"
                    m_f = show_map(ll_spn, 'map')
                    img = pygame.image.load(m_f).convert()
        screen.blit(img, (0, 0))
        pygame.display.update()
    os.remove(m_f)
    pygame.quit()


if __name__ == "__main__":
    main()

