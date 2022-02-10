"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest


from django.test import TestCase
from museum_site.datum import *


class DatumTest(unittest.TestCase):
    def test_text_datum(self):
        d = TextDatum(
            tag="customtag", kind="css_class",
            label="Filename", value="ZZT.zip",
            title="customtitle",
        )
        rendered = d.render()
        answer = '<customtag class="datum css_class">\n    <div class="label">Filename</div>\n    <div class="value"title="customtitle">ZZT.zip</div>\n</customtag>\n'
        self.assertEqual(rendered, answer)

    def test_link_datum(self):
        d = LinkDatum(
            tag="customtag", kind="css_class",
            label="My Label", value="My Value",
            url="https://example.website", target="_blank",
            roles=["classA", "classB"],
        )
        rendered = d.render()
        answer = '<customtag class="datum css_class">\n    <div class="label">My Label</div>\n    <div class="value"><a href="https://example.website" target="_blank" class=" classA classB">My Value</a></div>\n</customtag>\n'
        self.assertEqual(rendered, answer)

    def test_multi_link_datum(self):
        d = MultiLinkDatum(
            tag="customtag", kind="css_class",
            label="My Label",
            values=[
                dict(url="https://museumofzzt.com/", target="_blank", text="Museum of ZZT"),
                dict(url="https://digitalmzx.net/", text="It's Dot Com!"),
            ],
            url="https://example.website", target="_blank",
        )
        rendered = d.render()
        answer = '<customtag class="datum css_class">\n    <div class="label">My Label</div>\n    <div class="value"><a href="https://museumofzzt.com/" target="_blank">Museum of ZZT</a>, <a href="https://digitalmzx.net/" target="_blank">It&#x27;s Dot Com!</a></div>\n</customtag>\n'
        self.assertEqual(rendered, answer)

    def test_language_links_datum(self):
        d = LanguageLinksDatum(
            tag="span", kind="lang-links",
            label="Language",
            url="/language?lang=",
            values=[
                ("English", "en"),
                ("German", "de"),
                ("Other", "xx"),
            ],
            plural="S!",
            target="_blank",
        )
        rendered = d.render()
        answer = '<span class="datum lang-links">\n    <div class="label">LanguageS!</div>\n    <div class="value"><a href="/language?lang=en" target="_blank">English</a>, <a href="/language?lang=de" target="_blank">German</a>, <a href="/language?lang=xx" target="_blank">Other</a></div>\n</span>\n'
        self.assertEqual(rendered, answer)

    def test_ssv_links_datum(self):
        d = SSVLinksDatum(
            tag="span", kind="ssv-links",
            label="SSV",
            url="/ssv/",
            values=["typeA", "typeB", "typeC"],
            plural="ies",
            target="_blank",
        )
        rendered = d.render()
        answer = '<span class="datum ssv-links">\n    <div class="label">SSVies</div>\n    <div class="value"><a href="/ssv/typeA" target="_blank">typeA</a>, <a href="/ssv/typeB" target="_blank">typeB</a>, <a href="/ssv/typeC" target="_blank">typeC</a></div>\n</span>\n'
        self.assertEqual(rendered, answer)
