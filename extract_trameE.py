import pdb
import re
import csv

start = False
import time

global cpt
cpt = 0
import os

import csv


def get_time_stamp(value):
    return int(time.mktime(time.strptime(value, "%d/%m/%Y %H/%M/%S")))


class Trame:
    def __init__(self, d, path_file):
        self.path_file = path_file.replace(',', '_')
        self.identificateur = d[0]
        self.numero_formule = d[1]
        self.time = "%s/%s/%s" % (d[2], d[3], d[4])
        self.date = "%s/%s/%s" % (d[179], d[180], d[181])
        self.is_stop = d[167]
        self.time_stop = "%s%s%s" % (d[168], d[169], d[170])
        self.debit_production = float(d[162])
        self.time_stamp = get_time_stamp(self.date + ' ' + self.time)
        self.date_display = "%s/%s/%s %s:%s:%s" % ( d[179], d[180], d[181], d[2], d[3], d[4])


def handleTrame(data):
    if re.match('^E,', data):
        data_clean = re.sub('\|\n|\s+', '', data).split(',')
        if len(data_clean) > 180:
            return data_clean
            # else:
            # print "error %s" % (len(data_clean))
    return []


def get_raw_data(file_name):
    file_data = open(file_name)
    trams = []
    temp = ""
    for line in file_data:
        if re.match('^[a-zA-Z]+,', line):
            result = handleTrame(temp)
            if result:
                trams.append(handleTrame(temp))
            temp = line
        else:
            temp += line
    return trams


def create_list_object(data, path_file):
    result = []
    for d in data:
        try:
            trame_object = Trame(d, path_file)
            result.append(trame_object)
        except:
            pass
    return result


def calculate_total(data):
    temp = 0

    def calculate_production(e1, e2):
        # print e2.debit_production
        result = e2.debit_production * (e2.time_stamp - e1.time_stamp) / 3600
        return result

    for i in range(len(data) - 2):
        temp += calculate_production(data[i], data[i + 1])
    return temp


def filter_doublicate(data):
    keys = []
    result = []
    cpt = 0
    for i in data:
        if i.time_stamp not in keys:
            result.append(i)
            keys.append(i.time_stamp)
        else:
            cpt += 1
    print "Doublicate %s" % (cpt)
    return result


def write_to_csv(file_name, data):
    csvfile = open(file_name, 'wb')
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['Nom du fichier ', 'Identificateur', 'Date Heure', 'Debit'])
    for i in data:
        csvwriter.writerow([i.path_file, i.identificateur, i.date_display, i.debit_production])
    csvfile.close()


import shutil


def ensure_dir(directory):
    if directory:
        if not os.path.exists(directory):
            os.makedirs(directory)


def get_list_object_filter(dir, date_from, date_to, pattern_name=None, path_raw_data=None):
    ensure_dir(path_raw_data)
    t1_ = get_time_stamp(date_from)
    t2_ = get_time_stamp(date_to)
    result = []
    result_filter_date = []
    result_filter_dublicate = []
    result_order = []
    cpt = 0
    for output_file in os.listdir(dir):
        cpt += 1
        sub_result = []
        sub_result_filter_date = []
        if re.search(pattern_name, output_file):
            sub_result += create_list_object(get_raw_data(dir + '\\' + output_file), output_file)
        for item in sub_result:
            if (item.time_stamp >= t1_ and item.time_stamp <= t2_):
                sub_result_filter_date.append(item)
        if sub_result_filter_date:
            result_filter_date += sub_result_filter_date
            if path_raw_data:
                shutil.copy2(dir + '\\' + output_file, path_raw_data)

    result_filter_dublicate = filter_doublicate(result_filter_date)
    result_order = sorted(result_filter_dublicate, key=lambda k: k.time_stamp)
    return result_order


if __name__ == "__main__":
    raw_data_cp = "88025102"
    pattern_name = "_88025102"
    source = "C:\\Users\\nvbang\\Desktop\\raw_data"
    analyse_file = "analyse_trameE_21_05.csv"
    t1 = "21/05/2015 00/00/00"
    t2 = "21/05/2015 23/59/59"
    object_list = get_list_object_filter(source, t1, t2, pattern_name, raw_data_cp)
    total_p = calculate_total(object_list)
    csvfile = open(analyse_file, 'wb')
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['Nom du fichier ', 'Identificateur', 'Date Heure', 'Debit Production'])
    for i in object_list:
        csvwriter.writerow([i.path_file, i.identificateur, i.date_display, i.debit_production])
    csvwriter.writerow(['Total Production', total_p])
    csvfile.close()
    print "cpt %s" % (cpt)
    print total_p





	