import re
from flask import Flask, render_template, make_response, request

app = Flask(__name__)
application = app


@app.route('/')
def index():
    url = request.url
    return render_template('index.html', url=url)


@app.route('/args')
def args():
    return render_template('args.html')


@app.route('/headers')
def headers():
    return render_template('headers.html')


@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html'))
    response.set_cookie('biscuit', value='100 gramm')
    return response


@app.route('/form', methods=['POST', 'GET'])
def form():
    return render_template('form.html')


@app.route('/phone', methods=['POST', 'GET'])
def phone():
    error = ''
    result = ''
    if request.method == 'POST':
        tel = request.form.get('tel')
        match = re.search(r'^(?P<start>\+7|8?)(?P<other>.+)', tel)
        nums = ''.join(re.findall(r'\d', match.group('other')))
        chars = set(re.findall(r'\D', match.group('other')))
        result = f'8-{nums[:3]}-{nums[4:6]}-{nums[6:8]}-{nums[8:10]}'

        if len(nums) != 10:
            error = 'Неверное количество цифр.'
            result = 'ошибка'
        if not chars < set('() +.-'):
            error = 'В номере телефона встречаются недопустимые символы.'
            result = 'ошибка'

        
    return render_template('phone.html', error=error, result=result)
