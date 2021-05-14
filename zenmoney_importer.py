#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import datetime
import io
import json
import sys


def import_from_zen_money(fr):
    start_time = datetime.datetime.now()
    print('Import started %s' % str(start_time))

    lines = fr.readlines()

    count = float(len(lines) - 1)
    index = 0.0

    reader = csv.reader(lines[1:], delimiter=str(';'), quotechar=str('"'))

    output = {}

    accounts = {}
    accounts_id = 0
    categories = {}
    categories_id = 0
    payees = {}
    payees_id = 0
    currencies = {}
    currencies_id = 0
    transactions = []

    for row in reader:
        (date,
         category_name,
         payee_name,
         comment,
         outcome_account_name,
         outcome,
         outcome_currency_short_title,
         income_account_name,
         income,
         income_currency_short_title,
         created,
         modified,
         qr_code) = tuple(row)

        date_object = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')

        outcome_sum = outcome.replace(',', '.') if len(outcome) > 0 else 0.0
        income_sum = income.replace(',', '.') if len(income) > 0 else 0.0

        if outcome_sum == income_sum and (outcome_account_name == 'Долги' or income_account_name == 'Долги') and income_currency_short_title != outcome_currency_short_title:
            if outcome_currency_short_title == 'UAH':
                outcome_currency_short_title = income_currency_short_title
            elif income_currency_short_title == 'UAH':
                income_currency_short_title = outcome_currency_short_title

        if len(category_name) > 0:
            if category_name not in categories:
                categories_id += 1
                category_id = categories_id
                categories[category_name] = {'id': category_id,
                                             'name': category_name}
            else:
                category_id = categories[category_name]['id']
        else:
            category_id = None

        if len(payee_name) > 0:
            if payee_name not in payees:
                payees_id += 1
                payee_id = payees_id
                payees[payee_name] = {'id': payee_id,
                                      'name': payee_name}
            else:
                payee_id = payees[payee_name]['id']
        else:
            payee_id = None

        if len(income_currency_short_title) > 0:
            if income_currency_short_title not in currencies:
                currencies_id += 1
                income_currency_id = currencies_id
                currencies[income_currency_short_title] = {'id': income_currency_id,
                                                           'name': income_currency_short_title}
            else:
                income_currency_id = currencies[income_currency_short_title]['id']
        else:
            income_currency_id = None

        if len(income_account_name) > 0:
            name = 'Debts ' + income_currency_short_title if income_account_name == 'Долги' else income_account_name
            if name not in accounts:
                accounts_id += 1
                income_account_id = accounts_id
                accounts[name] = {'id': income_account_id,
                                  'name': name,
                                  'currency': income_currency_id}
            else:
                income_account_id = accounts[name]['id']
        else:
            income_account_id = None

        if len(outcome_currency_short_title) > 0:
            if outcome_currency_short_title not in currencies:
                currencies_id += 1
                outcome_currency_id = currencies_id
                currencies[outcome_currency_short_title] = {'id': outcome_currency_id,
                                                            'name': outcome_currency_short_title}
            else:
                outcome_currency_id = currencies[outcome_currency_short_title]['id']
        else:
            outcome_currency_id = None

        if len(outcome_account_name) > 0:
            name = 'Debts ' + outcome_currency_short_title if outcome_account_name == 'Долги' else outcome_account_name
            if name not in accounts:
                accounts_id += 1
                outcome_account_id = accounts_id
                accounts[name] = {'id': outcome_account_id,
                                  'name': name,
                                  'currency': outcome_currency_id}
            else:
                outcome_account_id = accounts[name]['id']
        else:
            outcome_account_id = None

        transaction_type = 'UNKNOWN'
        if payee_id:
            if income_account_id:
                if len([account for account in accounts.values() if
                        account['id'] == outcome_account_id and account['name'].startswith('Debts')]) > 0:
                    transaction_type = 'BORROW'
                else:
                    transaction_type = 'LEND'
            elif outcome_account_id:
                if len([account for account in accounts.values() if
                        account['id'] == income_account_id and account['name'].startswith('Debts')]) > 0:
                    transaction_type = 'LEND'
                else:
                    transaction_type = 'BORROW'
        elif income_account_id == outcome_account_id and float(income_sum) > 0 and float(outcome_sum) == 0:
            transaction_type = 'INCOME'
        elif outcome_account_id == income_account_id and float(income_sum) == 0 and float(outcome_sum) > 0:
            transaction_type = 'OUTCOME'
        else:
            transaction_type = 'TRANSFER'

        transactions.append({
            'type': transaction_type,
            'comment': comment,
            'date': str(date_object),
            'category': category_id,
            'output_sum': outcome_sum,
            'income_sum': income_sum,
            'payee': payee_id,
            'income_account': income_account_id,
            'outcome_account': outcome_account_id
        })

        index += 1
        s = 'Progress %0.2f%% (%0.0f/%0.0f)' % (index / count * 100.0, index, count)
        sys.stdout.write('\r' + s)

    finish_time = datetime.datetime.now()

    print ('\nImport finished %s' % str(finish_time))
    print ('Time elapsed %f seconds.' % ((finish_time - start_time).total_seconds()))

    output['currencies'] = list(currencies.values())
    output['categories'] = list(categories.values())
    output['accounts'] = list(accounts.values())
    output['payees'] = list(payees.values())
    output['transactions'] = transactions

    with io.open('exported.json', 'w+') as json_file:
        data = json.dumps(output, ensure_ascii=False, indent=4, sort_keys=True)
        json_file.write(data)


if __name__ == '__main__':
    with open('import.csv', mode='r') as f:
        import_from_zen_money(f)
