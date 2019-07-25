from django.shortcuts import render
from django.http import HttpResponse
import requests, json
import retailcrm
import time


def home(request):
    meta_info = request.GET['meta']
    products_info = request.GET['products']
    meta = json.loads(meta_info)
    products = json.loads(products_info)
    ord_id = meta["id"]

    #Формирование лог файла
    render_log_file(meta, products)

    #Формирование параметров для апи запроса
    message, parameters = get_parameters(meta, products)

    #ответный апи запрос
    api_request(ord_id, parameters)

    return HttpResponse(message)


def get_parameters(meta, products):
    standart_deliv = ['1111']
    non_standart_deliv = ['3921', '8354', '2312', '5192', '1734', '9042', '2589']
    sum_retail_code = ""
    sum_purchase_code = ""
    count_code = ""
    sum_retail_val = 0
    sum_purchase_val = 0
    count_val = 0
    trig_number = meta['trigger']
    trig_letter = ""
    order_id = meta['id']
    message = ""

    if trig_number == "1":
        trig_letter = "f"
    elif trig_number == "2":
        trig_letter = "s"
    else:
        trig_letter = "t"

    #Формирование парметров для апи запроса
    for i in range(0, len(products)):
        article = products[i]["article"]
        if article in standart_deliv:
            sum_retail_code = "opdk_stand_" + trig_letter + "summ"
            sum_purchase_code = "opdk_stand_" + trig_letter + "summ_purch"
            count_code = "opdk_stand_" + trig_letter + "count"
            sum_retail_val += int(products[i]['price_retail'])
            sum_purchase_val += int(products[i]['price_purchase'])
            count_val = 1
            message = "Стандартная"
        elif article in non_standart_deliv:
            sum_retail_code = "opdk_nonstand_" + trig_letter + "summ"
            sum_purchase_code = "opdk_nonstand_" + trig_letter + "summ_purch"
            count_code = "opdk_nonstand_" + trig_letter + "count"
            sum_retail_val += int(products[i]['price_retail'])
            sum_purchase_val += int(products[i]['price_purchase'])
            count_val = 1
            message = " Нестандартная"
    parameters = {
        "sum_retail_val": sum_retail_val, "sum_retail_code": sum_retail_code,
        "count_val": count_val, "count_code": count_code,
        "sum_purchase_val": sum_purchase_val, "sum_purchase_code": sum_purchase_code
    }
    message += "Код розничной суммы " + sum_retail_code + "  " + str(sum_retail_val) + " Код количества  " + count_code + " " + str(count_val)
    return message, parameters


def render_log_file(meta, products):
    order_info = ""
    about = f'\nНомер заказы {meta["id"]}. Триггера №{meta["trigger"]}'
    for i in range(0, len(products)):
        order_info += f'\narcticle = {products[i]["article"]}, retail price = {products[i]["price_retail"]}'
        order_info += f' purchase price = {products[i]["price_purchase"]}'
        #file.write(f'arcticle = {products[i]["article"]}, price = {products[i]["price"]}\n')
    log_text = about + order_info

    with open('log.txt', 'a') as file:
        cur_time = time.strftime("%d.%m.%y %H:%M:%S", time.localtime())
        # file.write(f'{text}  {cur_time}\n')
        if log_text:
            file.write(f'\nOperation time {cur_time}\n')
            file.write(f'Operation detail {log_text}\n')

    return log_text


def api_request(order_id, args):
    client = retailcrm.v5('https://caloristika.retailcrm.ru', 'UpKLgSX3j9qu11uREZ2weBKzcMcA2iYp')
    order = {
        'id': order_id,
        'customFields': {
            args["sum_retail_code"]: args["sum_retail_val"],
            args["sum_purchase_code"]: args["sum_purchase_val"],
            args["count_code"]: args["count_val"]
        }
    }
    uid_type = 'id'
    result = client.order_edit(order, uid_type)
    #response = result.response.decode('utf-8')
    response = result.get_response()
    with open('log.txt', 'a') as file:
        file.write(f'API request completed\n') if response["success"] \
            else file.write(f'API request failed\n')


