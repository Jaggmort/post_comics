import requests
import os
import random
from dotenv import load_dotenv


def main():
    load_dotenv()
    ACCESS_TOKEN_VK = os.environ.get('ACCESS_TOKEN_VK')
    GROUP_ID = int(os.environ.get('GROUP_ID'))
    image_path = 'comix.png'
    text_path = 'comix.txt'
    version = '5.131'
    fetch_comix(image_path, text_path)
    upload_server_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    post_url = 'https://api.vk.com/method/wall.post'
    params = {'access_token': ACCESS_TOKEN_VK, 'v': version,
              'group_id': GROUP_ID,
              }
    upload_url = get_upload_url(upload_server_url, params)
    with open(image_path, 'rb') as file:
        image_url = upload_url
        file = {
            'photo': file,
            }
        uploaded_image = upload_image(image_url, file)
    save_params = {'group_id': GROUP_ID,
                   'photo': uploaded_image['photo'],
                   'server': uploaded_image['server'],
                   'hash': uploaded_image['hash'],
                   'access_token': ACCESS_TOKEN_VK,
                   'v': version
                   }
    owner_id, media_id = save_image(save_url, save_params)
    with open(text_path, 'r') as file:
        image_comment = file.read()
    post_params = {'access_token': ACCESS_TOKEN_VK,
                   'v': version,
                   'owner_id': -GROUP_ID,
                   'message': image_comment,
                   'attachments': f'photo{owner_id}_{media_id}',
                   'from_group': 1
                   }
    requests.post(post_url, post_params)
    delete_file(image_path)
    delete_file(text_path)


def get_upload_url(url, params):
    upload_response = requests.get(url, params)
    upload_response.raise_for_status()
    upload_url = upload_response.json()['response']['upload_url']    
    return upload_url


def upload_image(url, file):
    upload_response = requests.post(url, files=file)
    upload_response.raise_for_status()
    uploaded_image = upload_response.json()
    return uploaded_image


def save_image(url, params):
    save_response = requests.post(url, params=params)
    save_response.raise_for_status()
    owner_id = save_response.json()['response'][0]['owner_id']
    media_id = save_response.json()['response'][0]['id']
    return owner_id, media_id


def get_image(url, filename, params=''):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    return


def fetch_comix(image_path, text_path):
    base_url = 'https://xkcd.com/info.0.json'
    response_num = requests.get(base_url)
    maximum_images = response_num.json()['num']
    random_index = random.randint(0, maximum_images)
    current_url = f'https://xkcd.com/{random_index}/info.0.json'
    response = requests.get(current_url)
    response.raise_for_status()
    image_link = response.json()['img']
    image_comment = response.json()['alt']
    with open(text_path, 'w') as file:
        file.write(image_comment)
    get_image(image_link, image_path)
    return


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("Can not delete the file as it doesn't exists")


if __name__ == '__main__':
    main()
