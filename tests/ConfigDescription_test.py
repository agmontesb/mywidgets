# test_-*- coding: utf-8 -*-
import pytest

from mywidgets.Tools.aapt.ConfigDescription import ConfigDescription

@pytest.fixture
def config():
    return ConfigDescription()


def test_ParseFailWhenQualifiersAreOutOfOrder(config):
    assert not ConfigDescription.parse("en-sw600dp-ldrtl", config)
    assert not ConfigDescription.parse("land-en", config)
    assert not ConfigDescription.parse("hdpi-320dpi", config)


def test_ParseFailWhenQualifiersAreNotMatched(config):
    assert not ConfigDescription.parse("en-sw600dp-ILLEGAL", config)


def test_ParseFailWhenQualifiersHaveTrailingDash(config):
    assert not ConfigDescription.parse("en-sw600dp-land-", config)


def test_ParseBasicQualifiers(config):
    strCnfs = ["",
               "fr-land",
               "mcc310-pl-sw720dp-normal-long-port-night-"
               "xhdpi-keyssoft-qwerty-navexposed-nonav",
    ]
    vers = ['', '', '-v13']
    for strCnf, strVer in zip(strCnfs, vers):
        assert ConfigDescription.parse(strCnf + strVer, config)
        assert config.toString() == strCnf + strVer


def test_ParseLocales(config):
    strCnf = 'en-rUS'
    assert ConfigDescription.parse(strCnf, config)
    assert config.toString() == strCnf


def test_ParseQualifierAddedInApi13(config):
    strCnf = 'sw600dp'
    assert ConfigDescription.parse(strCnf, config)
    assert config.toString() == "sw600dp-v13"

    config = ConfigDescription()
    strCnf = 'sw600dp-v8'
    assert ConfigDescription.parse(strCnf, config)
    assert config.toString() == "sw600dp-v13"


