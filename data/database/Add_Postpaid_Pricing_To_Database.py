import pymysql

def remove_colors(string):
    string = string.replace("Space Gray", "")
    if string != 'iPhone SE Silver':
        string = string.replace("Silver", "")
    string = string.replace("Cobalt Blue", "")
    string = string.replace("Titanium", "")
    string = string.replace("Rose Gold", "")
    string = string.replace("Gold", "")
    string = string.replace("Black", "")
    string = string.replace("Red", "")
    string = string.replace("Samsung ", "")
    string = string.replace("Apple ", "")
    string = string.replace("Motorola ", "")
    string = string.replace('™', '')
    string = string.replace('®', '')
    string = string.replace(u'\xa0', u' ')
    string = string.replace('6S', '6s')
    string = string.replace('Note 8', 'Note8')
    return string


def add_postpaid_to_database(provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url,
                             date, time):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "insert into postpaid(provider, device, storage, monthly_price, onetime_price, retail_price, " \
            "contract_ufc, url, date, time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    args = (provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time)
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        cursor.close()
    finally:
        connection.commit()
        connection.close()


def remove_postpaid_duplicate(provider, device, storage, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "DELETE FROM postpaid WHERE provider = %s AND device = %s AND storage = %s AND date = %s;"
    args = (provider, device, storage, date)
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        cursor.close()
    finally:
        connection.commit()
        connection.close()