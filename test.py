import json
from unittest import TestCase
from main import app
import config
from flask_sqlalchemy import SQLAlchemy
import count_tags
from bs4 import BeautifulSoup

app.testing = True
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_TEST_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class test_unit_count_tags(TestCase):
    def test_make_request(self):
        self.assertEqual(count_tags.make_request('http://example.ru'), '')

    def test_calculate_with_tags(self):
        html = """
        <html>
            <p> Name1
            <a href="https://stackoverflow.com/"> href1 </a> !
            <a href="https://lenta.com"> href2 </a> !
            </p>
            <p> Name2
            <a href="https://stackoverflow.com/"> href3 </a> !
            <a href="https://lenta.com"> href4 </a> !
            </p>
        </html>
        """
        html = BeautifulSoup(html, 'html.parser')
        self.assertDictEqual(count_tags.calculate(html), {"p": 2, "a": 4, "html": 1})

    def test_calculate_not_valid(self):
        html = '<test'
        self.assertDictEqual(count_tags.calculate(html), {})

class test_integrations_url(TestCase):
    global expected_negative_id, expected_negative_format
    expected_negative_id = {'Message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.', 'Status': 404}
    expected_negative_format = {'Message': 'The browser (or proxy) sent a request that this server could not understand.', 'Status': 400}

    def setUpClass():
        # arrane test db
        db.engine.execute('''DELETE FROM Url''')
        db.engine.execute('''UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME="Url"''')
        db.engine.execute('''
        INSERT INTO Url (Value, Tags, IsDone, IsValid)
        VALUES ('site', '{"html": 0}', 1, 1)''')

    def setUp(self):
        self.app = app.test_client()

    def test_get_positive(self):
        expected = {'Id': 1, 'Value': 'site', 'html': 0, 'IsDone': True, 'IsValid': True}
        response = self.app.get('/url/1',
                                content_type='application/json')
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected
        )

    def test_get_negative_id(self):
        response = self.app.get('/url/-1',
                                content_type='application/json')
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected_negative_id
        )

    def test_get_negative_format(self):
        input = {'Value': 'test'}
        response = self.app.post('/url/',
                                content_type='application/xml',
                                data=json.dumps(input))
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected_negative_format
        )

    def test_post_positive(self):
        input = {'Value': 'test'}
        expected = {'Id': 2, 'Value': 'test', 'IsDone': True, 'IsValid': False}
        response = self.app.post('/url/',
                                content_type='application/json',
                                data=json.dumps(input))
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected
        )

    def test_put_positive(self):
        input = {'Id': 1, 'Value': 'site', 'body': 0, 'IsDone': True, 'IsValid': True}
        expected = {'Id': 1, 'Value': 'site', 'body': 0, 'IsDone': True, 'IsValid': True}
        response = self.app.put('/url/1',
                                content_type='application/json',
                                data=json.dumps(input))
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected
        )

    def test_put_negative_id(self):
        input = {'Id': -1, 'Value': 'site', 'body': 0, 'IsDone': True, 'IsValid': True}
        response = self.app.put('/url/-1',
                                content_type='application/json',
                                data=json.dumps(input))
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected_negative_id
        )

    def test_put_negative_format(self):
        input = {'Id': 1, 'Value': 'site', 'body': 0, 'IsDone': True, 'IsValid': True}
        response = self.app.put('/url/1',
                                content_type='application/xml',
                                data=json.dumps(input))
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected_negative_format
        )

    def test_delete_postivie(self):
        expected = {'Result': True}
        response = self.app.delete('/url/1',
                                content_type='application/json')
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected
        )

    def test_delete_negative_id(self):
        response = self.app.delete('/url/-1',
                                content_type='application/json')
        actual = json.loads(response.get_data().decode())
        self.assertDictEqual(
            actual,
            expected_negative_id
        )
