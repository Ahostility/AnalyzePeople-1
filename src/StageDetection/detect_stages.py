import json
import sys
import pprint

import pandas as pd

from .KeyWordsSearch import search_phrases
from .Preprocessing_tools import full_preprocess_text, prepare_files, open_text
from .constnats import key_phrase, key_meal, key_category, greeting_key, farewell_key, pay_key, \
    additional_key, new_key, order_key, operator_id, client_id, vacancy_key, key_answer
from ..dirs import STAGES_FILE, DATA_NORMALIZED_SELLER_DIR, DATA_NORMALIZED_CLIENT_DIR

STAGE_NAMING = {'приветствие': 'Greeting', 'новинка': 'OfferOfNewProductsOrPromotions', 'заказ': 'Order',
                'доп': 'AdditionalSales', 'оплата': 'Payment', 'прощание': 'CompletionSale'}
ADDITION_NAMING = {'соус': 'Sauces', 'напитк': 'Drinks', 'пив': 'Drinks', 'пепс кол': 'Drinks',
                   'десерт': 'Desserts', 'основн': 'Garnishes', 'гарнир': 'Garnishes', 'завтрак': 'Garnishes',
                   'салат': 'Garnishes', 'закуск': 'Snacks', 'букет и снекбокс': 'Snacks', 'проч': 'Etc',
                   'проч товар': 'Etc', 'игрушк': 'Etc',
                   'доп': 'Etc', 'холодн напитк': 'Drinks', 'горяч напитк': 'Drinks'
                   }


def format_result(final_stages_time, vacancy_response, additional_sell, additional_sell_response,
                  additional_sale_adequacy, missed_addition, missed_addition_list):
    result = {}
    result['Vacancy'] = {'VacancyAvailability': int(len(final_stages_time[vacancy_key]) > 0),
                         'Result': 0}
    if len(vacancy_response) > 0:
        result['Vacancy']['Result'] = int(vacancy_response[1] == 'положительн')
    final_stages_time.pop(vacancy_key)
    result['Script'] = {STAGE_NAMING[x]: int(len(final_stages_time[x]) != 0) for x in final_stages_time.keys()}
    for k in final_stages_time.keys():
        if result['Script'][STAGE_NAMING[k]] != 0:
            result['Script'][f'{STAGE_NAMING[k]}Time'] = final_stages_time[k][1] - final_stages_time[k][0]
        else:
            result['Script'][f'{STAGE_NAMING[k]}Time'] = 0.0

    result['AdditionalSales'] = {}

    for group in ADDITION_NAMING.keys():
        result['AdditionalSales'][ADDITION_NAMING[group]] = {'Proposed': 0, 'Successful': 0, 'Adequate': 0, 'Missed': 0}

    if len(additional_sell) > 0:
        for group in additional_sell[1]:
            result['AdditionalSales'][ADDITION_NAMING[group]]['Proposed'] = 1
            if len(additional_sell_response) > 0 and result['AdditionalSales'][ADDITION_NAMING[group]]['Proposed']:
                result['AdditionalSales'][ADDITION_NAMING[group]]['Successful'] = int(
                    additional_sell_response[1] == 'agree')
            if len(additional_sale_adequacy) > 0 and result['AdditionalSales'][ADDITION_NAMING[group]]['Proposed']:
                result['AdditionalSales'][ADDITION_NAMING[group]]['Adequate'] = int(
                    additional_sale_adequacy[0] == 'ok')

            result['AdditionalSales'][ADDITION_NAMING[group]]['Missed'] = 0
    else:
        for group in ADDITION_NAMING.values():
            result['AdditionalSales'][group]['Successful'] = 0
            result['AdditionalSales'][group]['Adequate'] = 0
            result['AdditionalSales'][group]['Missed'] = int(
                any([ADDITION_NAMING[miss] == group for miss in missed_addition_list]))

    return result


def parse_diarization_file(file_name):
    all_phrases = open_text(file_name).split('\n')
    operator_name = all_phrases[0].strip()
    res = {client_id: [], operator_id: []}
    max_time = 0.0
    for seconds_text in all_phrases[1:]:
        if seconds_text == '':
            continue
        start_end_text = seconds_text.split(', ')
        max_time = float(start_end_text[1])
        res[int(start_end_text[2])].append([float(start_end_text[0]), max_time,
                                            full_preprocess_text(start_end_text[3])])

    return res, max_time


def search_stage(full_text, file_stage):
    all_info = pd.read_excel(file_stage, engine='openpyxl')
    key_words = list(all_info[key_phrase].dropna().values)
    return search_phrases(full_text, key_words)


def update_stages_id(stages_id, files, full_text, key):
    for file in files:
        found_ids = search_stage(full_text, DATA_NORMALIZED_SELLER_DIR / file)
        if len(found_ids) > 0:
            stages_id[key] += found_ids
    if len(stages_id[key]) > 0:
        new_ids = list(stages_id[key][0])
        for i in range(1, len(stages_id[key])):
            new_ids[1] = stages_id[key][i][1]
        stages_id[key] = new_ids


def check_missed_addition(file, order):
    all_info = pd.read_excel(file, engine='openpyxl')
    order_category = find_order_category(DATA_NORMALIZED_SELLER_DIR / 'category_menu.xlsx', order)
    res = set()
    for index, row in all_info.iterrows():
        if row['Order_category'] == order_category[0]:
            if type(row['Ok']) == str:
                res.add(row['Ok'])
    return res


def check_adequacy(file, order, additional):
    all_info = pd.read_excel(file, engine='openpyxl')
    order_category = find_order_category(DATA_NORMALIZED_SELLER_DIR / 'category_menu.xlsx', order)
    additional_category = find_order_category(DATA_NORMALIZED_SELLER_DIR / 'category_menu.xlsx', additional)
    ok = []
    not_ok = []
    for index, row in all_info.iterrows():
        if row['Order_category'] == order_category[0]:
            if type(row['Ok']) == str:
                ok.append(row['Ok'])
            if type(row['Not_ok']) == str:
                not_ok.append(row['Not_ok'])
    res = ['UNK'] * len(additional_category)
    for i, cat in enumerate(additional_category):
        if cat in ok:
            res[i] = 'ok'
        if cat in not_ok:
            res[i] = 'not_ok'
    return res


def find_order_category(file, order):
    all_info = pd.read_excel(file, engine='openpyxl')
    meal_cat = {}
    for index, row in all_info.iterrows():
        meal_cat[row['Key_phrase']] = row['Category']
    ids = search_phrases(order, list(meal_cat.keys()), interfere_thresh=0)
    res = []
    for id in ids:
        res.append(order[id[0]:id[1]].strip())
    return [meal_cat[x] for x in res]


def find_additional_response(files, stage_text):
    all_info = pd.DataFrame(columns=['Key_phrase', 'category'])
    for file in files:
        tmp = pd.read_excel(DATA_NORMALIZED_CLIENT_DIR / file, engine='openpyxl')
        tmp['category'] = pd.Series([file.split('.')[0].split('_')[1]] * len(tmp))
        all_info = pd.concat([all_info, tmp], axis=0)
    all_info = all_info.dropna()
    response_cat = dict()
    for index, row in all_info.iterrows():
        response_cat[row['Key_phrase']] = row['category']
    ids = search_phrases(stage_text, list(response_cat.keys()), interfere_thresh=0)
    res = []
    for id in ids:
        res.append(stage_text[id[0]:id[1]].strip())
    return res, [response_cat[x] for x in res]


def find_vacancy_response(file, stage_text):
    all_info = pd.read_excel(DATA_NORMALIZED_SELLER_DIR / file, engine='openpyxl')
    all_info = all_info.drop([key_phrase], axis=1).dropna()
    response_cat = dict()
    for index, row in all_info.iterrows():
        response_cat[row[key_answer]] = row[key_category]
    ids = search_phrases(stage_text, list(response_cat.keys()))
    res = []
    for id in ids:
        res.append(stage_text[id[0]:id[1]].strip())
    return res, [response_cat[x] for x in res]


def find_additional_cat(file, stage_text):
    all_info = pd.read_excel(DATA_NORMALIZED_SELLER_DIR / file, engine='openpyxl')
    all_info = all_info.drop([key_phrase], axis=1).dropna()
    meal_cat = dict()
    for index, row in all_info.iterrows():
        meal_cat[row[key_meal]] = row[key_category]
    ids = search_phrases(stage_text, list(meal_cat.keys()), interfere_thresh=0)
    res = []
    for id in ids:
        res.append(stage_text[id[0]:id[1]].strip())
    return res, [meal_cat[x] for x in res]


def parse_stage_file():
    stages_info = open_text(STAGES_FILE).split('\n')
    stage_files = dict()
    for stage in stages_info:
        name_files = stage.split('|')
        stage_files[name_files[0]] = name_files[1]
    return stage_files


def find_client_stages_id(full_text, stage_files):
    stages_to_find = [greeting_key, farewell_key, pay_key]
    stages_id = dict()
    for name_stage in stage_files.keys():
        files = stage_files[name_stage].split(';')
        stages_id[name_stage] = []
        update_stages_id(stages_id, files, full_text, name_stage)
    return stages_id


def find_operator_stages_id(full_text, stage_files):
    stages_id = dict()
    for name_stage in stage_files.keys():
        files = stage_files[name_stage].split(';')
        stages_id[name_stage] = []
        update_stages_id(stages_id, files, full_text, name_stage)
    if len(stages_id[additional_key]) != 0:
        if stages_id[pay_key] != 0:
            full_text = full_text[stages_id[additional_key][0]:stages_id[pay_key][0]]
        elif stages_id[farewell_key] != 0:
            full_text = full_text[stages_id[additional_key][0]:stages_id[farewell_key][0]]
        else:
            full_text = full_text[stages_id[additional_key][0]:]

    return stages_id


def get_full_text_speaker(speaker_time_text):
    full_text = ''
    id_time = dict()
    cur_id = 0
    for speech in speaker_time_text:
        full_text += speech[2] + ' ффф '
        id_time[(cur_id, len(full_text) - 4)] = speech[:2]
        cur_id = len(full_text) - 4
    full_text = full_text.strip()
    return full_text, id_time


def unite_op_client(time_op, time_cl):
    if len(time_op) == 0:
        return time_cl
    elif len(time_cl) == 0:
        return time_op
    return [min(time_op[0], time_cl[0]), max(time_op[1], time_cl[1])]


def id_to_time(ids, id_time):
    if len(ids) == 0:
        return []
    for key in id_time:
        if ids[0] >= key[0] and ids[1] <= key[1]:
            return id_time[key]
    return []


def get_order_time(new_time, additional_time):
    start = new_time
    end = additional_time
    if new_time[0] > additional_time[0]:
        start = additional_time
        end = new_time
    order_time = [start[1], end[0]]
    if order_time[1] < order_time[0]:
        order_time = [(start[0] + start[1]) / 2, (end[0] + end[1]) / 2]
    return order_time


def set_order_time(final_stages_time, max_time):
    key_1_vars = [new_key, greeting_key]
    key_2_vars = [additional_key, pay_key, farewell_key]
    time_1 = [0.0, 0.0]
    for key in key_1_vars:
        if len(final_stages_time[key]) != 0:
            time_1 = final_stages_time[key]
            break

    time_2 = [max_time, max_time]
    for key in key_2_vars:
        if len(final_stages_time[key]) != 0:
            time_2 = final_stages_time[key]
            break

    final_stages_time[order_key] = get_order_time(time_1, time_2)


def detect_stages(speaker_time_text, max_time):
    op_full_text, op_id_time = get_full_text_speaker(speaker_time_text[operator_id])
    client_full_text, client_id_time = get_full_text_speaker(speaker_time_text[client_id])

    stage_files = parse_stage_file()
    op_stages_id = find_operator_stages_id(op_full_text, stage_files)
    cl_stages_id = find_client_stages_id(client_full_text, stage_files)

    cl_stages_time = dict()
    op_stages_time = dict()
    for op_stage_id in op_stages_id:
        op_stages_time[op_stage_id] = id_to_time(op_stages_id[op_stage_id], op_id_time)
    for cl_stage_id in cl_stages_id:
        cl_stages_time[cl_stage_id] = id_to_time(cl_stages_id[cl_stage_id], client_id_time)

    final_stages_time = dict()
    final_stages_time[vacancy_key] = unite_op_client(cl_stages_time[vacancy_key], op_stages_time[vacancy_key])
    final_stages_time[pay_key] = unite_op_client(cl_stages_time[pay_key], op_stages_time[
        pay_key])  ### Объединяет найденные промежутки для оплаты
    final_stages_time[farewell_key] = unite_op_client(cl_stages_time[farewell_key],
                                                      op_stages_time[farewell_key])  ### прощания
    final_stages_time[greeting_key] = unite_op_client(cl_stages_time[greeting_key],
                                                      op_stages_time[greeting_key])  ### приветствия
    final_stages_time[new_key] = op_stages_time[new_key]  ### Берет только оператора для новинок
    final_stages_time[additional_key] = op_stages_time[additional_key]  ### и допов
    # if len(final_stages_time[pay_key]) != 0 and len(final_stages_time[additional_key]) != 0:
    # final_stages_time[additional_key][1] = final_stages_time[pay_key][1]
    set_order_time(final_stages_time, max_time)

    order = []
    for id in client_id_time:
        if client_id_time[id][0] >= final_stages_time[order_key][0] and client_id_time[id][1] <= \
                final_stages_time[order_key][1]:
            order = [id[0], id[1]]
            break

    additional_sell = []
    vacancy_response = []
    additional_sell_response = []
    additional_sale_adequacy = []
    if len(final_stages_time[additional_key]) != 0:
        res_id = []
        for id in op_id_time:
            if op_id_time[id][0] <= final_stages_time[additional_key][0] and op_id_time[id][1] >= \
                    final_stages_time[additional_key][1]:
                res_id = [id[0], id[1]]
                break

        additional_sell = find_additional_cat(
            stage_files[additional_key],
            op_full_text[res_id[0]:res_id[1]]
        )
        res_id = []
        for id in client_id_time:
            if client_id_time[id][0] >= final_stages_time[additional_key][0] and client_id_time[id][1] >= \
                    final_stages_time[additional_key][1]:
                res_id = [id[0], id[1]]
                break
        additional_sell_response = find_additional_response(['client_agree.xlsx', 'client_refusal.xlsx'],
                                                            client_full_text[res_id[0]:res_id[1]])
        addition = []
        for id in op_id_time:
            if op_id_time[id][0] >= final_stages_time[additional_key][0] and op_id_time[id][1] <= \
                    final_stages_time[additional_key][1]:
                addition = [id[0], id[1]]
                break
        additional_sale_adequacy = check_adequacy(DATA_NORMALIZED_SELLER_DIR / 'adequacy.xlsx',
                                                  client_full_text[order[0]:order[1]],
                                                  op_full_text[addition[0]:addition[1]])
    if len(final_stages_time[vacancy_key]) != 0:
        res_id = []
        for id in op_id_time:
            if op_id_time[id][0] >= final_stages_time[vacancy_key][0] and op_id_time[id][1] >= \
                    final_stages_time[vacancy_key][1]:
                res_id = [id[0], id[1]]
                break
        vacancy_response = find_vacancy_response(stage_files[vacancy_key], op_full_text[res_id[0]:res_id[1]])

    missed_addition = len(final_stages_time[additional_key]) == 0
    missed_addition_list = []
    if missed_addition and final_stages_time[order_key][0] != 0.0 and final_stages_time[order_key][1] != max_time:
        missed_addition_list = check_missed_addition(DATA_NORMALIZED_SELLER_DIR / 'adequacy.xlsx',
                                                     client_full_text[order[0]:order[1]])

    return format_result(final_stages_time, vacancy_response, additional_sell, additional_sell_response,
                         additional_sale_adequacy, missed_addition, missed_addition_list)


def main_pipeline(file_name, preprocess_source=False):
    if preprocess_source:
        prepare_files()
    speaker_time_text, max_time = parse_diarization_file(file_name)
    return detect_stages(speaker_time_text, max_time)



def write_result_to_json(pipe:dict,text_path:str) -> None:
    keys_json = list(pipe.keys())
    tandem = {'Vacancy':'vacancy','Script':'stage','AdditionalSales':'addSales'}
    for key in keys_json:
        name = pipe.get(key)
        json_pretty = write_json_on_key(key,name)
        with open(f'{tandem.get(key)}.json', 'w') as json_file:#Write to result json on keys
            json.dump(json_pretty, json_file, indent=4,sort_keys=False)
    with open(f'{text_path.split(".")[1].split("/")[-1]}.json', 'w') as json_file:#write of full resultjson on all keys
        json.dump(pipe, json_file,indent=4,sort_keys=True)


def write_json_on_key(key_json:str,contain_key:dict) -> dict:
    json_translate = {
        "Vacancy":{
            "Result":"quantity",
            "VacancyAvailability":"responseResult"
        },
        "Script":{
            "Greeting": "greeting",
            "OfferOfNewProductsOrPromotions": "newProductOffer",
            "Order": "order",
            "AdditionalSales": "addSales",
            "Payment": "payment",
            "CompletionSale": "parting",
            # "OfferOfNewProductsOrPromotionsTime":"example",
            #            "OrderTime": "order1",
        },
        "AdditionalSales":{
            "Drinks": "drinks",
            "Sauces": "sauces",
            "Desserts": "dessert",
            "Garnishes": "garnish",
            "Snacks": "snacks",
            "Promotions": "promotions",
            "Etc": "other",
        },
    }
    result_json = dict()

    for i in range(len(json_translate.get(key_json))):
        new_values = contain_key.get(list(json_translate.get(key_json).keys())[i])
        new_key = json_translate.get(key_json).get(list(json_translate.get(key_json).keys())[i])
        result_json.update({new_key:new_values})

    if key_json == "Vacancy":
        return result_json

    elif key_json == "Script":
        stage = {"stage":[]}
        for i in range(len(result_json)):
            stage.get("stage").append(
                {
                    "name": list(result_json.keys())[i],
                    "execution": result_json.get(list(result_json.keys())[i])
                }
            )
        return stage

    elif key_json == "AdditionalSales":
        additionales = {"addSales":[]}
        for i in range(len(result_json)):
            try:
                additionales.get("addSales").append(
                    {
                        "name": list(result_json.keys())[i],
                        "Proposed":dict(result_json.get(list(result_json.keys())[i])).get('Proposed'),
                        "Successful": dict(result_json.get(list(result_json.keys())[i])).get("Successful"),
                        "Adequate": dict(result_json.get(list(result_json.keys())[i])).get("Adequate"),
                        "Missed": dict(result_json.get(list(result_json.keys())[i])).get("Missed")
                    }
                )
            except TypeError:
                additionales.get("addSales").append(
                    {
                        "name": list(result_json.keys())[i],
                        "Proposed": 0,
                        "Successful": 0,
                        "Adequate":0,
                        "Missed":0
                    }
                )
        return additionales



if __name__ == '__main__':
    main_pipe = main_pipeline(sys.argv[1],True)
    write_result_to_json(main_pipe,sys.argv[1])


#----------------not Delete----------------------
    # json_res = json.dumps(main_pipe)
    # print(json.loads(json_res))

    # with open(f'{sys.argv[1].split(".")[0]}.json', 'w') as json_file:
# ----------------not Delete----------------------


    # with open(f'{sys.argv[1].split(".")[1].split("/")[-1]}.json', 'w') as json_file:
    #     json.dump(main_pipe, json_file)