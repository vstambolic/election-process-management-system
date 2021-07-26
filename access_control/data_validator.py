from abc import ABC, abstractmethod
import re
import datetime

from db_models import User


class Validator(ABC):
    data = ''

    def __init__(self, data):
        self.data = data

    @abstractmethod
    def is_valid(self, data):
        pass


class JMBGValidator(Validator):

    def __init__(self, jmbg):
        super().__init__(jmbg)

    def is_valid(self):
        match = re.search(
            r'^([0-3])([0-9])([0-1])([0-9])([0-9])([0-9])([0-9])([7-9])([0-9])([0-9])([0-9])([0-9])([0-9])$',
            self.data
        )
        if match is None:  # Invalid Format
            return False

        a = int(match.group(1))
        b = int(match.group(2))
        c = int(match.group(3))
        d = int(match.group(4))
        e = int(match.group(5))
        f = int(match.group(6))
        g = int(match.group(7))
        h = int(match.group(8))
        i = int(match.group(9))
        j = int(match.group(10))
        k = int(match.group(11))
        l = int(match.group(12))
        m = int(match.group(13))

        checksum = 11 - ((7 * (a + g) + 6 * (b + h) + 5 * (c + i) + 4 * (d + j) + 3 * (e + k) + 2 * (f + l)) % 11)
        checksum = checksum if checksum < 10 else 0
        if checksum != m:  # Invalid checksum
            return False

        day = a * 10 + b
        month = c * 10 + d
        millennium = 2000 if e == 0 else 1000

        year = millennium + e * 100 + f * 10 + g

        try:
            datetime.datetime(year, month, day)
        except ValueError:
            return False  # Invalid date

        return True

    def is_unique(self):
        return User.query.filter(User.jmbg == self.data).first() is None


class EmailValidator(Validator):

    def __init__(self, email):
        super().__init__(email)

    def is_valid(self):
        match = re.search(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            self.data
        )
        return match is not None and len(self.data) <256

    def is_unique(self):
        return User.query.filter(User.email == self.data).first() is None


class PasswordValidator(Validator):

    def __init__(self, password):
        super().__init__(password)

    def is_valid(self):

        return 8 <= len(self.data) < 256 \
               and re.search(f'\d', self.data) \
               and re.search(f'[a-z]',self.data)\
               and re.search(f'[A-Z]', self.data)


