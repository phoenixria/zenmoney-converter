#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import datetime
import io
import json
import sys


def import_from_zen_money(fr):
    start_time = datetime.datetime.now()
    print 'Import started %s' % str(start_time)

    lines = fr.readlines()

    count = float(len(lines))
    index = 0.0

    reader = csv.reader(lines, delimiter=str(','), quotechar=str('"'))

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
         modified) = tuple(row)

        date_object = datetime.datetime.strptime(created.decode('utf-8-sig'), '%Y-%m-%d %H:%M:%S')

        outcome_sum = outcome.replace(',', '.') if len(outcome) > 0 else 0.0
        income_sum = income.replace(',', '.') if len(income) > 0 else 0.0

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
            if income_account_name not in accounts:
                accounts_id += 1
                income_account_id = accounts_id
                accounts[income_account_name] = {'id': income_account_id,
                                                 'name': income_account_name,
                                                 'currency': income_currency_id}
            else:
                income_account_id = accounts[income_account_name]['id']
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
            if outcome_account_name not in accounts:
                accounts_id += 1
                outcome_account_id = accounts_id
                accounts[outcome_account_name] = {'id': outcome_account_id,
                                                  'name': outcome_account_name,
                                                  'currency': outcome_currency_id}
            else:
                outcome_account_id = accounts[outcome_account_name]['id']
        else:
            outcome_account_id = None

        transaction_type = 'UNKNOWN'
        if payee_id:
            if income_account_id:
                transaction_type = 'BORROW'
            elif outcome_account_id:
                transaction_type = 'LEND'
        elif income_account_id and not outcome_account_id:
            transaction_type = 'INCOME'
        elif outcome_account_id and not income_account_id:
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

    print '\nImport finished %s' % str(finish_time)
    print 'Time elapsed %f seconds.' % ((finish_time - start_time).total_seconds())

    output['currencies'] = currencies.values()
    output['categories'] = categories.values()
    output['accounts'] = accounts.values()
    output['payees'] = payees.values()
    output['transactions'] = transactions

    with io.open('exported.json', 'w+', encoding='utf8') as json_file:
        data = json.dumps(output, ensure_ascii=False, encoding='utf8', indent=4, sort_keys=True)
        json_file.write(unicode(data))


if __name__ == '__main__':
    with open('import.csv', mode='r') as f:
        import_from_zen_money(f)
