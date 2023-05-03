import xml.etree.ElementTree as ET
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# # Создаем  скелет датафрейма
shapka = {'Кадастровый № ОКС':[],'Вид ОКС':[],'Назначение':[],'Адрес ОКС':[],'Площадь':[],'ФИО':[],'Вид, номер, дата и время государственной регистрации права':[]}
df = pd.DataFrame(shapka)

# Функция получения словаря с данными из xml. Для добавления в пандас фрейм.
def data_from_xml(root):
    # Словарь для добавления строк с данными экселей, в датафрейм
    stroka = dict()
    # Список для фио
    sp = list()
    # Добавляем данные
    stroka['Кадастровый № ОКС'] = root[2][1][0][0].text
    stroka['Вид ОКС'] = "Здание"
    for znachenie_tag in root.iter('purpose'):
        for znach in znachenie_tag:
            if znach.tag == 'value':
                stroka['Назначение'] = znach.text
    for adress_tag in root.iter('address'):
        for adress in adress_tag:
            if adress.tag == 'readable_address':
                stroka['Адрес ОКС'] = adress.text
    for area_tag in root.iter('params'):
        for area in area_tag:
            if area.tag == 'area':
                stroka['Площадь'] = area.text

    for sobstsvennik_tag in root.iter('right_holder'):
        if len(sp) > 0:
            break
        for sobstsvennik in sobstsvennik_tag:
            if sobstsvennik.tag == 'individual':
                for fio_tag in root.iter('individual'):
                    for fio in fio_tag:
                        if fio.tag == 'surname':
                            sp.append(fio.text)
                        elif fio.tag == 'name':
                            sp.append(fio.text)
                        elif fio.tag == 'patronymic':
                            sp.append(fio.text)
                stroka['ФИО'] = '  '.join(sp)
                break
            if sobstsvennik.tag == 'public_formation':
                for municipal_tag in root.iter('municipality'):
                    for municipal in municipal_tag:
                        if municipal.tag == 'name':
                            stroka['ФИО'] = municipal.text
            if sobstsvennik.tag == 'legal_entity':
                for municipal_tag in root.iter('resident'):
                    for municipal in municipal_tag:
                        if municipal.tag == 'name':
                            stroka['ФИО'] = municipal.text
    vid_prava = list()
    number_prava = list()
    date_prava = list()
    for right_records_tag in root.iter('right_records'):
        for right_record in right_records_tag:
            data_prava = right_record[0][0].text[:-6]
            data_prava_clear = data_prava.replace('T',' ')
            date_prava.append(data_prava_clear)
            vid_prava.append(right_record[1][0][1].text)
            number_prava.append(right_record[1][1].text)
    x = zip(vid_prava,number_prava,date_prava)
    y = [', '.join(i) for i in x]
    stroka['Вид, номер, дата и время государственной регистрации права'] = '  '.join(y)
    return stroka

for papka in os.scandir(r'.//Общая'):
    spispok_xml = os.listdir(fr'.//Общая/{papka.name}')
    for xml in spispok_xml:
        print(f'В работе {xml}')
        tree = ET.parse(fr'.//Общая/{papka.name}/{xml}')
        root = tree.getroot()
        df = pd.concat([df, pd.DataFrame.from_records([data_from_xml(root)])] ,ignore_index=True)



# Для просто записи датафрейма в эксель, без обработки листов
df.to_excel(r'.//Данные из xml.xlsx', index= False)