# coding:utf-8
import re
import sys
import datetime
import urllib
import requests
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

now = datetime.datetime.now().strftime('%Y-%m-%d')
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}
url = 'http://210.45.88.100'
session = requests.session()
session.headers = headers


def check_network():
    print('Check network...'),
    r = session.get(url)
    if r.status_code == 200:
        print('success!')
    else:
        raise Exception('error!')


def input_login():
    data_login = {
        'username': raw_input("Please input username："),
        'password': raw_input("Please input password："),
        'rememberusername': '0',
        'anchor': ''
    }
    return data_login


def parse_login():
    data_login = input_login()
    r = session.post(url + '/login/index/php', data_login)
    soup = BeautifulSoup(r.text, 'lxml')
    r = soup.find(id='loginerrormessage')
    if r is None:
        return True
    else:
        print(r.text)
        return False


def parse_my():
    print('Login...'),
    r = session.get(url + '/my/index/php')
    soup = BeautifulSoup(r.text, 'lxml')
    course = soup.find('section').find_all('a', href=re.compile('[^"].*?/course/view.php\?id=.*?[^"]'))
    print('success!'),
    print(soup.find(class_='usertext').text)
    for q in course:
        print('Catch course'),
        print(q.text),
        a = raw_input('(y/n)?')
        if a == 'y' or a == 'Y':
            return re.search('id=(\d*)', q.attrs['href']).group(1), q.text
    sys.exit(0)


def parse_course(course):
    r = session.get(url + '/course/view.php?id=' + course)
    soup = BeautifulSoup(r.text, 'lxml')
    quiz = soup.find('a', href=re.compile('[^"].*?/mod/quiz/view.php\?id=.*?[^"]'))
    return re.search('id=(\d*)', quiz.attrs['href']).group(1)


def parse_quiz(quiz):
    print('.'),
    r = session.get(url + '/mod/quiz/view.php?id=' + quiz)
    soup = BeautifulSoup(r.text, 'lxml')
    cmid = soup.find(attrs={'name': 'cmid'}).attrs['value']
    sesskey = soup.find(attrs={'name': 'sesskey'}).attrs['value']
    data_startattempt = {
        'cmid': cmid,
        'sesskey': sesskey,
        '_qf__mod_quiz_preflight_check_form': '1',
        'submitbutton': urllib.quote('开始答题'.encode('utf-8'))
    }
    print('.'),
    r = session.post(url + '/mod/quiz/startattempt.php', data_startattempt)
    soup = BeautifulSoup(r.text, 'lxml')
    attempt = soup.find('a', href=re.compile('[^"].*?/mod/quiz/attempt.php\?attempt=.*?[^"]'))
    attempt = re.search('attempt=(\d*)', attempt.attrs['href']).group(1)
    data_processattempt = {
        'attempt': attempt,
        'finishattempt': '1',
        'timeup': '0',
        'slots': '',
        'sesskey': sesskey
    }
    print('.'),
    session.post(url + '/mod/quiz/processattempt.php', data_processattempt)
    return attempt


def parse_review(attempt, lesson):
    print('.'),
    page = 0
    repeat = 1
    n_pd = 0
    n_dx = 0
    n_ddx = 0
    f_pd = open('%s %s pd.txt' % (lesson, now), 'a+')
    f_dx = open('%s %s dx.txt' % (lesson, now), 'a+')
    f_ddx = open('%s %s ddx.txt' % (lesson, now), 'a+')
    f_pd.seek(0)
    f_dx.seek(0)
    f_ddx.seek(0)
    r_pd = f_pd.read()
    r_dx = f_dx.read()
    r_ddx = f_ddx.read()
    while True:
        r = session.get('%s/mod/quiz/review.php?attempt=%s&page=%s' % (url, attempt, str(page)))
        soup = BeautifulSoup(r.text, 'lxml')
        for q in soup.find_all('div', id=re.compile('q[\d*]')):
            if 'truefalse' in q.attrs['class']:
                if q.find(class_='qtext').text in r_pd:
                    continue
                else:
                    repeat = 0
                    n_pd = n_pd + 1
                    f_pd.write(q.find(class_='qtext').text + '\n')
                    f_pd.write(q.find(class_='rightanswer').text + '\n')
                    f_pd.write('\n')
            elif 'multichoice' in q.attrs['class']:
                if q.find(class_='qtext').text in r_dx:
                    continue
                else:
                    repeat = 0
                    n_dx = n_dx + 1
                    f_dx.write(q.find(class_='qtext').text + '\n')
                    for m in q.find_all(class_=re.compile('r[\d*]')):
                        f_dx.write(m.text + '\n')
                    f_dx.write(q.find(class_='rightanswer').text + '\n')
                    f_dx.write('\n')
            elif 'multichoiceset' in q.attrs['class']:
                if q.find(class_='qtext').text in r_ddx:
                    continue
                else:
                    repeat = 0
                    n_ddx = n_ddx + 1
                    f_ddx.write(q.find(class_='qtext').text + '\n')
                    for m in q.find_all(class_=re.compile('r[\d*]')):
                        f_ddx.write(m.text + '\n')
                    f_ddx.write(q.find(class_='rightanswer').text + '\n')
                    f_ddx.write('\n')
        if '/mod/quiz/view.php' in soup.find(id='region-main').find(class_='mod_quiz-next-nav').attrs['href']:
            f_pd.close()
            f_dx.close()
            f_ddx.close()
            break
        else:
            page = page + 1
    print('pd:' + str(n_pd)),
    print('dx:' + str(n_dx)),
    print('ddx:' + str(n_ddx)),
    return repeat


def main():
    try:
        num = 0
        repeat = 0
        tolerance = None
        check_network()
        while parse_login() is False:
            pass
        course, lesson = parse_my()
        quiz = parse_course(course)
        while tolerance is None:
            tolerance = re.match('\d', raw_input('Plase input the tolerance[0-9]:'))
        tolerance = int(tolerance.group())
        while repeat <= tolerance:
            num = num + 1
            print('Num:'+str(num)),
            print(str(repeat) + '<=' + str(tolerance)),
            attempt = parse_quiz(quiz)
            repeat_r = parse_review(attempt, lesson)
            if repeat_r == 0:
                repeat = 0
            else:
                repeat = repeat + repeat_r
            print('success')
        print('Done. All success')
    except Exception, e:
        print('Error:'),
        print(e)

if __name__ == '__main__':
    main()