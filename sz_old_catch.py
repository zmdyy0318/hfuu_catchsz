# coding:utf-8
import sys
import re
import requests
import datetime
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

now = datetime.datetime.now().strftime('%Y-%m-%d')
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}
url = 'http://210.45.88.213/exercise'
session = requests.session()
session.headers = headers

lesson = {
    '1': '马克思主义基本原理概论',
    '2': '毛中特（上）',
    '3': '中国近现代史纲要',
    '4': '思想道德修养与法律基础',
    '5': '党的基本知识',
    '6': '军事理论教程',
    '7': '毛中特（下）'
}


def check_sid(sid):
    print('Check sid...'),
    r = session.get(url+'/exercise.asp?courseID=1&sid=' + sid)
    if '/exercise/exercise.asp' in r.text:
        print('error!')
        return None
    else:
        print('success!')
        return sid


def check_network():
    print('Check network...'),
    r = session.get(url)
    if r.status_code == 200:
        print('success!')
    else:
        raise Exception('error!')


def parse_exercise(course_id, sid):
    repeat = 1
    n_pd = 0
    n_dx = 0
    n_ddx = 0
    f_pd = open('%s %s pd.txt' % (lesson[course_id], now), 'a+')
    f_dx = open('%s %s dx.txt' % (lesson[course_id], now), 'a+')
    f_ddx = open('%s %s ddx.txt' % (lesson[course_id], now), 'a+')
    f_pd.seek(0)
    f_dx.seek(0)
    f_ddx.seek(0)
    r_pd = f_pd.read()
    r_dx = f_dx.read()
    r_ddx = f_ddx.read()
    r = session.get(url+'/exercise.asp?courseID=%s&sid=%s' % (course_id, sid))
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'lxml')

    input_question = soup.find_all('input', id=re.compile('question\d+'))
    input_a = soup.find_all('input', id=re.compile('a\d+'))
    input_b = soup.find_all('input', id=re.compile('b\d+'))
    input_c = soup.find_all('input', id=re.compile('c\d+'))
    input_d = soup.find_all('input', id=re.compile('d\d+'))
    input_answer = soup.find_all('input', id=re.compile('answer\d+'))

    for q in input_question:
        question = q.attrs['value']
        answer = input_answer.pop(0).attrs['value']
        if answer.isdigit():
            if question in r_pd:
                continue
            else:
                repeat = 0
                n_pd = n_pd + 1
                f_pd.write(question + '\n')
                if answer == '0':
                    f_pd.write('正确的答案是“错”。' + '\n')
                elif answer == '1':
                    f_pd.write('正确的答案是“对”。' + '\n')
                f_pd.write('\n')
        elif len(answer) == 1:
            if question in r_dx:
                continue
            else:
                repeat = 0
                n_dx = n_dx + 1
                f_dx.write(question + '\n')
                f_dx.write('A. ' + input_a.pop(0).attrs['value'] + '\n')
                f_dx.write('B. ' + input_b.pop(0).attrs['value'] + '\n')
                f_dx.write('C. ' + input_c.pop(0).attrs['value'] + '\n')
                f_dx.write('D. ' + input_d.pop(0).attrs['value'] + '\n')
                f_dx.write('正确答案是：' + answer + '\n')
                f_dx.write('\n')
        elif len(answer) > 1:
            if question in r_ddx:
                continue
            else:
                repeat = 0
                n_ddx = n_ddx + 1
                f_ddx.write(question + '\n')
                f_ddx.write('A. ' + input_a.pop(0).attrs['value'] + '\n')
                f_ddx.write('B. ' + input_b.pop(0).attrs['value'] + '\n')
                f_ddx.write('C. ' + input_c.pop(0).attrs['value'] + '\n')
                f_ddx.write('D. ' + input_d.pop(0).attrs['value'] + '\n')
                f_ddx.write('正确答案是：' + answer + '\n')
                f_ddx.write('\n')
    f_pd.close()
    f_dx.close()
    f_ddx.close()
    print('pd:' + str(n_pd)),
    print('dx:' + str(n_dx)),
    print('ddx:' + str(n_ddx)),
    return repeat


def main():
    try:
        num = 0
        repeat = 0
        sid = None
        course_id = None
        tolerance = None
        check_network()
        while sid is None:
            sid = check_sid(raw_input('Please input sid(12010110xx):'))
        for i in lesson.keys():
            print('%s:%s' % (i, lesson[i]))
        while course_id is None:
            i = raw_input('Please input lesson ID:')
            if i not in lesson:
                continue
            else:
                course_id = i
        while tolerance is None:
            tolerance = re.match('\d', raw_input('Plase input the tolerance[0-9]:'))
        tolerance = int(tolerance.group())
        while repeat <= tolerance:
            num = num + 1
            print('Num:'+str(num)),
            print(str(repeat) + '<=' + str(tolerance)),
            repeat_r = parse_exercise(course_id, sid)
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