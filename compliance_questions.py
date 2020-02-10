import csv
from uuid import uuid4
import json

result_data = []

QUESTION = 0
YES = 1
NO = 2
IDENTIFIER = 3


def csv_data(path):
    def format_possible_offset(string):
        # if string is "1 Line below", will return 1. If string is "Class 1", will return "Class 1"
        s = string.split(" ", 1)
        if s[0].isdigit():
            return int(s[0])
        else:
            return string

    with open(path, 'r') as csv_file:
        data = []
        csv_reader = csv.reader(csv_file, delimiter=',')

        next(csv_reader, None)  # skip header during iteration

        for row in csv_reader:
            row[YES] = format_possible_offset(row[YES])
            row[NO] = format_possible_offset(row[NO])
            data.append(row)

        return data


def create_json(row):
    data = {
        "id": str(uuid4()),
        "name": "test",
        "responses": [
            {
                "a": 1
            }
        ]
    }


if __name__ == '__main__':
    print(csv_data('./compliance-questions-formatted.csv'))



