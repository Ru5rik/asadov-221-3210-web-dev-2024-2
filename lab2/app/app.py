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
    if request.method == 'POST':
        tel = request.form.get('tel')
        # full
        # "^(\+7|8)[\s+()-.]*(\d{3})[\s+()-.]*(\d{3})[\s+()-.]*(\d\d)[\s+()-.]*(\d\d)"gm
        
        # nums
        # ^(\+7|8)([\D]*)([\d]*)([\D]*)([\d]*)([\D]*)([\d]*)([\D]*)([\d]*)
        
        # gibrid
        # ^(\+7|8)([\D]*)(\d{,3})([\D]*)(\d{,3})([\D]*)(\d{,2})([\D]*)(\d{,2})
        
        match = re.search(r'^(?P<start>\+7|8*)(?P<other>.+)', tel)
        nums = ''.join(re.findall(r'\d', match.group('other')))
        chars = set(re.findall(r'\D', match.group('other')))

        if len(nums) != 10:
            error = 'Неверное количество цифр.'
        if not chars < set('() +.-'):
            error = 'В номере телефона встречаются недопустимые символы.'
            
        result = f'8-{nums[:3]}-{nums[4:6]}-{nums[6:8]}-{nums[8:10]}'
        
    return render_template('phone.html', error=error, result=result)
