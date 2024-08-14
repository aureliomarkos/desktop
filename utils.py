# coding=utf-8
import re
from datetime import datetime, timedelta
from qt_core import QBrush, QFont, QColor

# pegar o ano e o mês de refrencia da parcela
def get_mes_ano_referencia(data):
    mes = data.month - 1
    ano = data.year

    if mes == 0:
        mes = 12
        ano = ano - 1
    return mes, ano


# gera parcelas para contas a pagar e receber
def proximo_mes(diaVcto, data):

    proximo_mes = data.replace(day=1) + timedelta(days=32)  # Primeiro dia do próximo mês

    # Se o próximo mês for fevereiro, manter o mesmo dia da data inicial
    if proximo_mes.month == 2:
        dia = min(data.day, 28 if proximo_mes.year % 4 != 0 or (proximo_mes.year % 100 == 0 and proximo_mes.year % 400 != 0) else 29)
        proximo_mes = proximo_mes.replace(day=dia)
    else:
        proximo_mes = proximo_mes.replace(day=diaVcto)  # Mesmo dia do mês anterior ao próximo mês
    return proximo_mes


# set color table row
def set_table_row_color(row, tableWidget, ativo=None):
    for col in range(tableWidget.columnCount()):
        item = tableWidget.item(row, col)

        if item is not None:
            if row % 2 == 0:   
                # color white
                item.setBackground(QBrush(QColor(255, 255, 255)))
                item.setForeground(QBrush(QColor(0, 0, 0)))
            else:
                # color grey
                item.setBackground(QBrush(QColor(225, 225, 225)))
                item.setForeground(QBrush(QColor(0, 0, 0)))
            
            if ativo == False:
                # color red
                item.setBackground(QBrush(QColor(255, 0, 0)))
                item.setForeground(QBrush(QColor(255, 255, 255)))

            font = QFont()
            #font.setBold(True)
            font.setPixelSize(12)
            item.setFont(font)


# get values data table
def get_values_data_table(tableWidget):

    table_data = []
    for row in range(tableWidget.rowCount()):
        row_data = []
        for column in range(tableWidget.columnCount()):
            item = tableWidget.item(row, column)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append("")
        table_data.append(row_data)
    return table_data


# validate cep
def validate_cep(cep):
    # Verifica a formatação do CPF
    if not re.match(r'\d{5}-\d{3}', cep):
        return False
    else:
        return True


# validate email
def validate_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(email_regex, email):
        return True
    else:
        return False