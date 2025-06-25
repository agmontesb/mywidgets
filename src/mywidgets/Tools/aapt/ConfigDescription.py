# -*- coding: utf-8 -*-
#
# ported from:
# https://android.googlesource.com/platform/frameworks/base/+/1ab598f/tools/aapt2/ConfigDescription.cpp
#
import re
import ctypes
from functools import wraps

import Tools.aapt.AconfigurationConst as AconfigurationConst
from Tools.aapt.ResourcesTypes import ResTable_config

SDK_CUPCAKE = 3
SDK_DONUT = 4
SDK_ECLAIR = 5
SDK_ECLAIR_0_1 = 6
SDK_ECLAIR_MR1 = 7
SDK_FROYO = 8
SDK_GINGERBREAD = 9
SDK_GINGERBREAD_MR1 = 10
SDK_HONEYCOMB = 11
SDK_HONEYCOMB_MR1 = 12
SDK_HONEYCOMB_MR2 = 13
SDK_ICE_CREAM_SANDWICH = 14
SDK_ICE_CREAM_SANDWICH_MR1 = 15
SDK_JELLY_BEAN = 16
SDK_JELLY_BEAN_MR1 = 17
SDK_JELLY_BEAN_MR2 = 18
SDK_KITKAT = 19
SDK_KITKAT_WATCH = 20
SDK_LOLLIPOP = 21
SDK_LOLLIPOP_MR1 = 22

wildcardName = "any"


# def anyDecorator(func):
#     @wraps(func)
#     def wrapper(strIn, config):
#         try:
#             parseStr, outStr = strIn.split('-', 1)
#         except:
#             parseStr, outStr = strIn, ''
#         if func(parseStr, config):
#             return outStr
#         return strIn
#     return wrapper

def anyDecorator(func):
    @wraps(func)
    def wrapper(strIn, config):
        try:
            parseStr, outStr = strIn.split('-', 1)
        except:
            parseStr, outStr = strIn, ''
        className = func.__name__[len('parse'):]
        if ResTable_config.BaseEnum.hasEnum(className):
            field = className[0].lower() + className[1:]
            try:
                parseStr = ResTable_config.BaseEnum.getInstance(parseStr, field=field)
            except:
                if field != 'density': return strIn
        if func(parseStr, config):
            return outStr
        return strIn

    return wrapper


@anyDecorator
def parseMcc(parseStr, config):
    if parseStr == wildcardName:
        config.mcc = 0
        return True
    if not parseStr.startswith('mcc') or len(parseStr) != 6:
        return False
    try:
        config.mcc = int(parseStr[3:])
        return True
    except:
        return False


@anyDecorator
def parseMnc(parseStr, config):
    if parseStr == wildcardName:
        config.mcc = 0
        return True
    if not parseStr.startswith('mnc') or len(parseStr) == 3 or len(parseStr) > 6:
        return False
    try:
        ival = int(parseStr[3:])
        config.mnc = ival or AconfigurationConst.ACONFIGURATION_MNC_ZERO
        return True
    except:
        return False


def parseLocale(parseStr, config):
    try:
        locStr, outStr = parseStr.split('-', 1)
    except:
        locStr, outStr = parseStr, ''
    if locStr[0] == 'b' and locStr[1] == '+':
        #  This is a "modified" BCP-47 language tag. Same semantics as BCP-47 tags,
        #  except that the separator is "+" and not "-".
        subtags = locStr.split('+')[1:]
        nlen = len(subtags)
        if nlen >= 1:
            config.language = subtags[0].lower()
        if nlen == 2:
            case = len(subtags[1])
            if case in [2, 3]:
                config.country = subtags[1].upper()
            elif case == 4:
                config.localeScript = subtags[1].title()
            elif case in [5, 6, 7, 8]:
                config.localeVariant = subtags[1]
            else:
                return parseStr
        elif nlen == 3:
            if len(subtags[1]) == 4:
                config.localeScript = subtags[1].title()
            elif len(subtags[1]) in [2, 3]:
                config.country = subtags[1]
            else:
                return parseStr

            if len(subtags[2]) > 4:
                config.localeVariant = subtags[2]
            elif len(subtags[1]) in [2, 3]:
                config.country = subtags[2].upper()
        elif nlen == 4:
            config.language = subtags[0].lower()
            config.localeScript = subtags[1].title()
            config.country = subtags[2].upper()
            config.localeVariant = subtags[3]
        else:
            return parseStr
        return outStr
    else:
        if len(locStr) in [2, 3] and locStr.isalpha() and locStr != 'car':
            config.language = locStr.lower()
            try:
                locStr, outStr = outStr.split('-', 1)
            except:
                locStr, outStr = outStr, ''
            if locStr and locStr[0] == 'r' and len(locStr) == 3:
                config.country = locStr[1:].upper()
                return outStr
            else:
                return locStr + '-' + outStr
    return parseStr


@anyDecorator
def parseLayoutDir(layoutattr, config):
    config.layoutDir = layoutattr
    return True


@anyDecorator
def parseSmallestScreenWidthDp(parseStr, config):
    if parseStr == wildcardName:
        config.smallestScreenWidthDp = ResTable_config.SCREENWIDTH_ANY
        return True
    if not parseStr.startswith('sw') or not parseStr.endswith('dp'):
        return False
    try:
        config.smallestScreenWidthDp = int(parseStr[2:-2])
    except:
        return False
    return True


@anyDecorator
def parseScreenWidthDp(parseStr, config):
    if parseStr == wildcardName:
        config.screenWidthDp = ResTable_config.SCREENWIDTH_ANY
        return True
    if not parseStr.startswith('w') or not parseStr.endswith('dp'):
        return False
    try:
        config.screenWidthDp = int(parseStr[1:-2])
    except:
        return False
    return True


@anyDecorator
def parseScreenHeightDp(parseStr, config):
    if parseStr == wildcardName:
        config.screenHeightDp = ResTable_config.SCREENHEIGHT_ANY
        return True
    if not parseStr.startswith('h') or not parseStr.endswith('dp'):
        return False
    try:
        config.screenHeightDp = int(parseStr[1:-2])
    except:
        return False
    return True


@anyDecorator
def parseScreenLayoutSize(layoutattr, config):
    config.screenLayoutSize = layoutattr
    return True


@anyDecorator
def parseScreenLayoutLong(layoutattr, config):
    config.screenLayoutLong = layoutattr
    return True


@anyDecorator
def parseScreenLayoutRound(layoutattr, config):
    config.screenLayoutRound = layoutattr
    return True


@anyDecorator
def parseHdr(layoutattr, config):
    config.hdr = layoutattr
    return True


@anyDecorator
def parseWideColorGamut(layoutattr, config):
    config.wideColorGamut = layoutattr
    return True


@anyDecorator
def parseOrientation(layoutattr, config):
    config.orientation = layoutattr
    return True


@anyDecorator
def parseUiModeType(layoutattr, config):
    config.uiModeType = layoutattr
    return True


@anyDecorator
def parseUiModeNight(layoutattr, config):
    config.uiModeNight = layoutattr
    return True


@anyDecorator
def parseDensity(layoutattr, config):
    if isinstance(layoutattr, (bytes, str)):
        if not layoutattr.upper().endswith('DPI'):
            return False
        try:
            layoutattr = int(layoutattr[:-3])
        except:
            return False
    config.density = layoutattr
    return True


@anyDecorator
def parseTouchscreen(layoutattr, config):
    config.touchscreen = layoutattr
    return True


@anyDecorator
def parseKeysHidden(layoutattr, config):
    config.keysHidden = layoutattr
    return True


@anyDecorator
def parseKeyboard(layoutattr, config):
    config.keyboard = layoutattr
    return True


@anyDecorator
def parseNavHidden(layoutattr, config):
    config.navHidden = layoutattr
    return True


@anyDecorator
def parseNavigation(layoutattr, config):
    config.navigation = layoutattr
    return True


@anyDecorator
def parseScreenSize(parseStr, config):
    if parseStr == wildcardName:
        w = ResTable_config.SCREENWIDTH_ANY
        h = ResTable_config.SCREENHEIGHT_ANY
    else:
        try:
            x, y = parseStr.split('x')
        except:
            return False

        try:
            w = int(x)
            h = int(y)
            if w < h:
                return False
        except:
            return False
    config.screenwidth = w
    config.screenHeight = h
    return True


@anyDecorator
def parseVersion(parseStr, config):
    if parseStr == wildcardName:
        config.sdkVersion = ResTable_config.SDKVERSION_ANY
        config.minorVersion = ResTable_config.MINORVERSION_ANY
        return True
    if not parseStr.startswith('v'):
        return False
    try:
        config.sdkVersion = int(parseStr[1:])
        config.minorVersion = 0
    except:
        return False
    return True


class ConfigDescription(ResTable_config):
    @staticmethod
    def parse(strIn, configDescription):
        '''
        Parse a string of the form 'fr-sw600dp-land' and fill in the
        given ResTable_config with resulting configuration parameters.
        The resulting configuration has the appropriate sdkVersion defined
        for backwards compatibility.
        :param strIn: String: String to parse.
        :param configDescription: ConfigDescription: Parse result.
        :return: boolean: True if no error occur while parsing, else False.
        '''
        if strIn.endswith('-'): return False
        pArray = (parseMcc, parseMnc, parseLocale, parseLayoutDir,
                  parseSmallestScreenWidthDp, parseScreenWidthDp, parseScreenHeightDp,
                  parseScreenLayoutSize, parseScreenLayoutLong, parseScreenLayoutRound,
                  parseHdr, parseWideColorGamut, parseOrientation,
                  parseUiModeType, parseUiModeNight, parseDensity, parseTouchscreen,
                  parseKeysHidden, parseKeyboard, parseNavHidden, parseNavigation,
                  parseScreenSize, parseVersion,)
        pMax = len(pArray)
        pPos = 0 if strIn else None
        while strIn and pPos < pMax:
            strIn = pArray[pPos](strIn, configDescription)
            pPos += 1
        if strIn and pPos == pMax:
            return False
        if pPos is not None:
            ConfigDescription.applyVersionForCompatibility(configDescription)
        return True

    @staticmethod
    def applyVersionForCompatibility(config):
        minSdk = 0
        rtc = ResTable_config
        if config.density == rtc.DENSITY_ANY:
            minSdk = SDK_LOLLIPOP
        elif config.smallestScreenWidthDp != rtc.SCREENWIDTH_ANY or \
                config.screenWidthDp != rtc.SCREENWIDTH_ANY or \
                config.screenHeightDp != rtc.SCREENHEIGHT_ANY:
            minSdk = SDK_HONEYCOMB_MR2
        elif (config.uiMode & rtc.MASK_UI_MODE_TYPE) != rtc.UI_MODE_TYPE_ANY or \
                (config.uiMode & rtc.MASK_UI_MODE_NIGHT) != rtc.UI_MODE_NIGHT_ANY:
            minSdk = SDK_FROYO
        elif (config.screenLayout & rtc.MASK_SCREENSIZE) != rtc.SCREENSIZE_ANY or \
                (config.screenLayout & rtc.MASK_SCREENLONG) != rtc.SCREENLONG_ANY or \
                config.density != rtc.DENSITY_DEFAULT:
            minSdk = SDK_DONUT

        if minSdk > config.sdkVersion:
            config.sdkVersion = minSdk