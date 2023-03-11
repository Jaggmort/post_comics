import requests
import os
import random
from dotenv import load_dotenv


def main():
    load_dotenv()
    vk_access_token = os.environ.get('VK_ACCESS_TOKEN')
    group_id = int(os.environ.get('VK_GROUP_ID'))
    image_path = 'comix.png'
    version = '5.131'
    try:
        image_comment = fetch_comix(image_path)
        upload_url = get_upload_url(vk_access_token, version, group_id)
        uploaded_image = upload_image(upload_url, image_path)
        photo = upload_image['photo']
        server = upload_image['server']
        hash = upload_image['hash']
        owner_id, media_id = save_image(group_id,
                                        photo,
                                        server,
                                        hash,
                                        vk_access_token,
                                        version
                                        )
        post_comics(image_comment, vk_access_token,
                    version,
                    group_id,
                    f'photo{owner_id}_{media_id}'
                    )
    finally:
        delete_file(image_path)


def check_vk_answer(decoded):
    if decoded['error']:
        raise Exception(decoded['error']['error_msg'])


def get_upload_url(vk_access_token, version, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {'access_token': vk_access_token, 'v': version,
              'group_id': group_id,
              }
    upload_response = requests.get(url, params=params)
    upload_response.raise_for_status()
    decoded_upload_response = upload_response.json()
    check_vk_answer(decoded_upload_response)
    upload_url = decoded_upload_response['response']['upload_url']
    return upload_url


def post_comics(image_comment, vk_access_token,
                version,
                group_id,
                photo_ids
                ):
        url = 'https://api.vk.com/method/wall.post'        
        post_params = {'access_token': vk_access_token,
                       'v': version,
                       'owner_id': -group_id,
                       'message': image_comment,
                       'attachments': photo_ids,
                       'from_group': 1
                       }
        response = requests.post(url, post_params)
        decoded_response = response.json()
        check_vk_answer(decoded_response)


def upload_image(url, image_path):
    with open(image_path, 'rb') as file:
        file = {
                'photo': file,
                }
        upload_response = requests.post(url, files=file)
    upload_response.raise_for_status()
    uploaded_image = upload_response.json()
    check_vk_answer(uploaded_image)
    return uploaded_image


def save_image(group_id, photo, server, hash, vk_access_token, version):
    save_params = {'group_id': group_id,
                   'photo': photo,
                   'server': server,
                   'hash': hash,
                   'access_token': vk_access_token,
                   'v': version
                   }
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_response = requests.post(url, params=save_params)
    save_response.raise_for_status()
    decoded_save_response = save_response.json()
    check_vk_answer(decoded_save_response)
    owner_id = decoded_save_response['response'][0]['owner_id']
    media_id = decoded_save_response['response'][0]['id']
    return owner_id, media_id


def get_image(url, filename, params=''):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def fetch_comix(image_path):
    base_url = 'https://xkcd.com/info.0.json'
    base_response = requests.get(base_url)
    maximum_images = base_response.json()['num']
    random_index = random.randint(0, maximum_images)
    current_url = f'https://xkcd.com/{random_index}/info.0.json'
    response = requests.get(current_url)
    response.raise_for_status()
    decoded_response = response.json()
    image_link = decoded_response['img']
    image_comment = decoded_response['alt']
    get_image(image_link, image_path)
    return image_comment


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


if __name__ == '__main__':
    main()
