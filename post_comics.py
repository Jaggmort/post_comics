import requests
import os
import random
from dotenv import load_dotenv


def main():
    load_dotenv()
    ACCESS_TOKEN_VK = os.environ.get('ACCESS_TOKEN_VK')
    GROUP_ID = int(os.environ.get('GROUP_ID'))
    image_path = 'Images/comix.png'
    text_path = 'Images/comix.txt'
    version = '5.131'
    fetch_comix(image_path, text_path)
    upload_server_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    post_url = 'https://api.vk.com/method/wall.post'
    params = {'access_token': ACCESS_TOKEN_VK, 'v': version,
              'group_id': GROUP_ID,
              }
    upload_response = requests.get(upload_server_url, params)
    upload_response.raise_for_status()
    upload_url = upload_response.json()['response']['upload_url']
    with open('images/comix.png', 'rb') as file:
        image_url = upload_url
        files = {
            'photo': file,
            }
        upload_response = requests.post(image_url, files=files)
        upload_response.raise_for_status()
    uploaded_image = upload_response.json()
    save_params = {'group_id': GROUP_ID,
                   'photo': uploaded_image['photo'],
                   'server': uploaded_image['server'],
                   'hash': uploaded_image['hash'],
                   'access_token': ACCESS_TOKEN_VK,
                   'v': version
                   }
    save_response = requests.post(save_url, params=save_params)
    owner_id = save_response.json()['response'][0]['owner_id']
    media_id = save_response.json()['response'][0]['id']
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
