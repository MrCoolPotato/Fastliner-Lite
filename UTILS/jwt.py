import requests


'''def generate_jitsi_jwt_token(conference_id, user_display_name, access_token):

    url = 'http://57.129.70.186:5000/generate-jwt'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'conference_id': conference_id}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        token = response.json().get('token')
        if token:
            signals.messageSignal.emit("JWT token generated successfully.", "success")
            return token
        else:
            signals.messageSignal.emit("JWT token generation failed: No token received.", "error")
            return None
    except requests.exceptions.RequestException as e:
        signals.messageSignal.emit("Error obtaining JWT token.", "error")
        return None    '''