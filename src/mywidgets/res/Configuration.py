# -*- coding: utf-8 -*-
"""
https://developer.android.com/reference/android/content/res/Configuration
ported from:
https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/content/res/Configuration.java
"""
from Android import overload
from Android.content.pm.ActivityInfo import ActivityInfo
from Android.interface.IParcelable import IParcelable
from Android._Os.LocaleList import LocaleList

class Configuration(IParcelable):
    """
    This class describes all device configuration information that can impact
    the resources the application retrieves. This includes both user-specified
    configuration options (locale list and scaling) as well as device
    configurations (such as input modes, screen size and screen orientation).
    """
    """
    public static final int COLOR_MODE_HDR_MASK:
    Constant for colorMode: bits that encode the dynamic range of the screen. 
    """
    COLOR_MODE_HDR_MASK = 0x0000000c

    """
    public static final int COLOR_MODE_HDR_NO:
    Constant for colorMode: a COLOR_MODE_HDR_MASK value
    indicating that the screen is not HDR (low/standard dynamic range).
    Corresponds to the -lowdr resource qualifier.
    """
    COLOR_MODE_HDR_NO = 0x00000004

    """
    public static final int COLOR_MODE_HDR_SHIFT:
    Constant for colorMode: bits shift to get the screen dynamic range. 
    """
    COLOR_MODE_HDR_SHIFT = 0x00000002

    """
    public static final int COLOR_MODE_HDR_UNDEFINED:
    Constant for colorMode: a COLOR_MODE_HDR_MASK value
    indicating that it is unknown whether or not the screen is HDR.
    """
    COLOR_MODE_HDR_UNDEFINED = 0x00000000

    """
    public static final int COLOR_MODE_HDR_YES:
    Constant for colorMode: a COLOR_MODE_HDR_MASK value
    indicating that the screen is HDR (dynamic range).
    Corresponds to the -highdr resource qualifier.
    """
    COLOR_MODE_HDR_YES = 0x00000008

    """
    public static final int COLOR_MODE_UNDEFINED:
    Constant for colorMode: a value indicating that the color mode is 
    undefined 
    """
    COLOR_MODE_UNDEFINED = 0x00000000

    """
    public static final int COLOR_MODE_WIDE_COLOR_GAMUT_MASK:
    Constant for colorMode: bits that encode whether the screen is wide gamut. 
    """
    COLOR_MODE_WIDE_COLOR_GAMUT_MASK = 0x00000003

    """
    public static final int COLOR_MODE_WIDE_COLOR_GAMUT_NO:
    Constant for colorMode: a COLOR_MODE_WIDE_COLOR_GAMUT_MASK value
    indicating that the screen is not wide gamut.
    Corresponds to the -nowidecg resource qualifier.
    """
    COLOR_MODE_WIDE_COLOR_GAMUT_NO = 0x00000001

    """
    public static final int COLOR_MODE_WIDE_COLOR_GAMUT_UNDEFINED:
    Constant for colorMode: a COLOR_MODE_WIDE_COLOR_GAMUT_MASK value
    indicating that it is unknown whether or not the screen is wide gamut.
    """
    COLOR_MODE_WIDE_COLOR_GAMUT_UNDEFINED = 0x00000000

    """
    public static final int COLOR_MODE_WIDE_COLOR_GAMUT_YES:
    Constant for colorMode: a COLOR_MODE_WIDE_COLOR_GAMUT_MASK value
    indicating that the screen is wide gamut.
    Corresponds to the -widecg resource qualifier.
    """
    COLOR_MODE_WIDE_COLOR_GAMUT_YES = 0x00000002

    """
    public static final int DENSITY_DPI_UNDEFINED:
    Default value for densityDpi indicating that no width
    has been specified.
    """
    DENSITY_DPI_UNDEFINED = 0x00000000

    """
    public static final int HARDKEYBOARDHIDDEN_NO:
    Constant for hardKeyboardHidden, value corresponding to the
    physical keyboard being exposed. 
    """
    HARDKEYBOARDHIDDEN_NO = 0x00000001

    """
    public static final int HARDKEYBOARDHIDDEN_UNDEFINED:
    Constant for hardKeyboardHidden: a value indicating that no value has been 
    set. 
    """
    HARDKEYBOARDHIDDEN_UNDEFINED = 0x00000000

    """
    public static final int HARDKEYBOARDHIDDEN_YES:
    Constant for hardKeyboardHidden, value corresponding to the
    physical keyboard being hidden. 
    """
    HARDKEYBOARDHIDDEN_YES = 0x00000002

    """
    public static final int KEYBOARDHIDDEN_NO:
    Constant for keyboardHidden, value corresponding to the
    keysexposed
    resource qualifier. 
    """
    KEYBOARDHIDDEN_NO = 0x00000001

    """
    public static final int KEYBOARDHIDDEN_UNDEFINED:
    Constant for keyboardHidden: a value indicating that no value has been 
    set. 
    """
    KEYBOARDHIDDEN_UNDEFINED = 0x00000000

    """
    public static final int KEYBOARDHIDDEN_YES:
    Constant for keyboardHidden, value corresponding to the
    keyshidden
    resource qualifier. 
    """
    KEYBOARDHIDDEN_YES = 0x00000002

    """
    public static final int KEYBOARD_12KEY:
    Constant for keyboard, value corresponding to the
    12key
    resource qualifier. 
    """
    KEYBOARD_12KEY = 0x00000003

    """
    public static final int KEYBOARD_NOKEYS:
    Constant for keyboard, value corresponding to the
    nokeys
    resource qualifier. 
    """
    KEYBOARD_NOKEYS = 0x00000001

    """
    public static final int KEYBOARD_QWERTY:
    Constant for keyboard, value corresponding to the
    qwerty
    resource qualifier. 
    """
    KEYBOARD_QWERTY = 0x00000002

    """
    public static final int KEYBOARD_UNDEFINED:
    Constant for keyboard: a value indicating that no value has been set. 
    """
    KEYBOARD_UNDEFINED = 0x00000000

    """
    public static final int MNC_ZERO:
    Constant used to to represent MNC (Mobile Network Code) zero.
    0 cannot be used, since it is used to represent an undefined MNC.
    """
    MNC_ZERO = 0x0000ffff

    """
    public static final int NAVIGATIONHIDDEN_NO:
    Constant for navigationHidden, value corresponding to the
    navexposed
    resource qualifier. 
    """
    NAVIGATIONHIDDEN_NO = 0x00000001

    """
    public static final int NAVIGATIONHIDDEN_UNDEFINED:
    Constant for navigationHidden: a value indicating that no value has been 
    set. 
    """
    NAVIGATIONHIDDEN_UNDEFINED = 0x00000000

    """
    public static final int NAVIGATIONHIDDEN_YES:
    Constant for navigationHidden, value corresponding to the
    navhidden
    resource qualifier. 
    """
    NAVIGATIONHIDDEN_YES = 0x00000002

    """
    public static final int NAVIGATION_DPAD:
    Constant for navigation, value corresponding to the
    dpad
    resource qualifier. 
    """
    NAVIGATION_DPAD = 0x00000002

    """
    public static final int NAVIGATION_NONAV:
    Constant for navigation, value corresponding to the
    nonav
    resource qualifier. 
    """
    NAVIGATION_NONAV = 0x00000001

    """
    public static final int NAVIGATION_TRACKBALL:
    Constant for navigation, value corresponding to the
    trackball
    resource qualifier. 
    """
    NAVIGATION_TRACKBALL = 0x00000003

    """
    public static final int NAVIGATION_UNDEFINED:
    Constant for navigation: a value indicating that no value has been set. 
    """
    NAVIGATION_UNDEFINED = 0x00000000

    """
    public static final int NAVIGATION_WHEEL:
    Constant for navigation, value corresponding to the
    wheel
    resource qualifier. 
    """
    NAVIGATION_WHEEL = 0x00000004

    """
    public static final int ORIENTATION_LANDSCAPE:
    Constant for orientation, value corresponding to the
    land
    resource qualifier. 
    """
    ORIENTATION_LANDSCAPE = 0x00000002

    """
    public static final int ORIENTATION_PORTRAIT:
    Constant for orientation, value corresponding to the
    port
    resource qualifier. 
    """
    ORIENTATION_PORTRAIT = 0x00000001

    """
    public static final int ORIENTATION_SQUARE:
    
    This constant was deprecated
    in API level 16.
    Not currently supported or used.
    """
    ORIENTATION_SQUARE = 0x00000003

    """
    public static final int ORIENTATION_UNDEFINED:
    Constant for orientation: a value indicating that no value has been set. 
    """
    ORIENTATION_UNDEFINED = 0x00000000

    """
    public static final int SCREENLAYOUT_LAYOUTDIR_LTR:
    Constant for screenLayout: a SCREENLAYOUT_LAYOUTDIR_MASK
    value indicating that a layout dir has been set to LTR. 
    """
    SCREENLAYOUT_LAYOUTDIR_LTR = 0x00000040

    """
    public static final int SCREENLAYOUT_LAYOUTDIR_MASK:
    Constant for screenLayout: bits that encode the layout direction. 
    """
    SCREENLAYOUT_LAYOUTDIR_MASK = 0x000000c0

    """
    public static final int SCREENLAYOUT_LAYOUTDIR_RTL:
    Constant for screenLayout: a SCREENLAYOUT_LAYOUTDIR_MASK
    value indicating that a layout dir has been set to RTL. 
    """
    SCREENLAYOUT_LAYOUTDIR_RTL = 0x00000080

    """
    public static final int SCREENLAYOUT_LAYOUTDIR_SHIFT:
    Constant for screenLayout: bits shift to get the layout direction. 
    """
    SCREENLAYOUT_LAYOUTDIR_SHIFT = 0x00000006

    """
    public static final int SCREENLAYOUT_LAYOUTDIR_UNDEFINED:
    Constant for screenLayout: a SCREENLAYOUT_LAYOUTDIR_MASK
    value indicating that no layout dir has been set. 
    """
    SCREENLAYOUT_LAYOUTDIR_UNDEFINED = 0x00000000

    """
    public static final int SCREENLAYOUT_LONG_MASK:
    Constant for screenLayout: bits that encode the aspect ratio. 
    """
    SCREENLAYOUT_LONG_MASK = 0x00000030

    """
    public static final int SCREENLAYOUT_LONG_NO:
    Constant for screenLayout: a SCREENLAYOUT_LONG_MASK
    value that corresponds to the
    notlong
    resource qualifier. 
    """
    SCREENLAYOUT_LONG_NO = 0x00000010

    """
    public static final int SCREENLAYOUT_LONG_UNDEFINED:
    Constant for screenLayout: a SCREENLAYOUT_LONG_MASK
    value indicating that no size has been set. 
    """
    SCREENLAYOUT_LONG_UNDEFINED = 0x00000000

    """
    public static final int SCREENLAYOUT_LONG_YES:
    Constant for screenLayout: a SCREENLAYOUT_LONG_MASK
    value that corresponds to the
    long
    resource qualifier. 
    """
    SCREENLAYOUT_LONG_YES = 0x00000020

    """
    public static final int SCREENLAYOUT_ROUND_MASK:
    Constant for screenLayout: bits that encode roundness of the screen. 
    """
    SCREENLAYOUT_ROUND_MASK = 0x00000300

    """
    public static final int SCREENLAYOUT_ROUND_NO:
    Constant for screenLayout: a SCREENLAYOUT_ROUND_MASK value indicating
    that the screen does not have a rounded shape.
    """
    SCREENLAYOUT_ROUND_NO = 0x00000100

    """
    public static final int SCREENLAYOUT_ROUND_UNDEFINED:
    Constant for screenLayout: a SCREENLAYOUT_ROUND_MASK value indicating
    that it is unknown whether or not the screen has a round shape.
    """
    SCREENLAYOUT_ROUND_UNDEFINED = 0x00000000

    """
    public static final int SCREENLAYOUT_ROUND_YES:
    Constant for screenLayout: a SCREENLAYOUT_ROUND_MASK value indicating
    that the screen has a rounded shape. Corners may not be visible to the 
    user;
    developers should pay special attention to the WindowInsets delivered
    to views for more information about ensuring content is not obscured.
    
    Corresponds to the -round resource qualifier.
    """
    SCREENLAYOUT_ROUND_YES = 0x00000200

    """
    public static final int SCREENLAYOUT_SIZE_LARGE:
    Constant for screenLayout: a SCREENLAYOUT_SIZE_MASK
    value indicating the screen is at least approximately 480x640 dp units,
    corresponds to the
    large
    resource qualifier.
    See Supporting
    Multiple Screens for more information. 
    """
    SCREENLAYOUT_SIZE_LARGE = 0x00000003

    """
    public static final int SCREENLAYOUT_SIZE_MASK:
    Constant for screenLayout: bits that encode the size. 
    """
    SCREENLAYOUT_SIZE_MASK = 0x0000000f

    """
    public static final int SCREENLAYOUT_SIZE_NORMAL:
    Constant for screenLayout: a SCREENLAYOUT_SIZE_MASK
    value indicating the screen is at least approximately 320x470 dp units,
    corresponds to the
    normal
    resource qualifier.
    See Supporting
    Multiple Screens for more information. 
    """
    SCREENLAYOUT_SIZE_NORMAL = 0x00000002

    """
    public static final int SCREENLAYOUT_SIZE_SMALL:
    Constant for screenLayout: a SCREENLAYOUT_SIZE_MASK
    value indicating the screen is at least approximately 320x426 dp units,
    corresponds to the
    small
    resource qualifier.
    See Supporting
    Multiple Screens for more information. 
    """
    SCREENLAYOUT_SIZE_SMALL = 0x00000001

    """
    public static final int SCREENLAYOUT_SIZE_UNDEFINED:
    Constant for screenLayout: a SCREENLAYOUT_SIZE_MASK
    value indicating that no size has been set. 
    """
    SCREENLAYOUT_SIZE_UNDEFINED = 0x00000000

    """
    public static final int SCREENLAYOUT_SIZE_XLARGE:
    Constant for screenLayout: a SCREENLAYOUT_SIZE_MASK
    value indicating the screen is at least approximately 720x960 dp units,
    corresponds to the
    xlarge
    resource qualifier.
    See Supporting
    Multiple Screens for more information.
    """
    SCREENLAYOUT_SIZE_XLARGE = 0x00000004

    """
    public static final int SCREENLAYOUT_UNDEFINED:
    Constant for screenLayout: a value indicating that screenLayout is 
    undefined 
    """
    SCREENLAYOUT_UNDEFINED = 0x00000000

    """
    public static final int SCREEN_HEIGHT_DP_UNDEFINED:
    Default value for screenHeightDp indicating that no width
    has been specified.
    """
    SCREEN_HEIGHT_DP_UNDEFINED = 0x00000000

    """
    public static final int SCREEN_WIDTH_DP_UNDEFINED:
    Default value for screenWidthDp indicating that no width
    has been specified.
    """
    SCREEN_WIDTH_DP_UNDEFINED = 0x00000000

    """
    public static final int SMALLEST_SCREEN_WIDTH_DP_UNDEFINED:
    Default value for smallestScreenWidthDp indicating that no width
    has been specified.
    """
    SMALLEST_SCREEN_WIDTH_DP_UNDEFINED = 0x00000000

    """
    public static final int TOUCHSCREEN_FINGER:
    Constant for touchscreen, value corresponding to the
    finger
    resource qualifier. 
    """
    TOUCHSCREEN_FINGER = 0x00000003

    """
    public static final int TOUCHSCREEN_NOTOUCH:
    Constant for touchscreen, value corresponding to the
    notouch
    resource qualifier. 
    """
    TOUCHSCREEN_NOTOUCH = 0x00000001

    """
    public static final int TOUCHSCREEN_STYLUS:
    
    This constant was deprecated
    in API level 16.
    Not currently supported or used.
    """
    TOUCHSCREEN_STYLUS = 0x00000002

    """
    public static final int TOUCHSCREEN_UNDEFINED:
    Constant for touchscreen: a value indicating that no value has been set. 
    """
    TOUCHSCREEN_UNDEFINED = 0x00000000

    """
    public static final int UI_MODE_NIGHT_MASK:
    Constant for uiMode: bits that encode the night mode. 
    """
    UI_MODE_NIGHT_MASK = 0x00000030

    """
    public static final int UI_MODE_NIGHT_NO:
    Constant for uiMode: a UI_MODE_NIGHT_MASK
    value that corresponds to the
    notnight
    resource qualifier. 
    """
    UI_MODE_NIGHT_NO = 0x00000010

    """
    public static final int UI_MODE_NIGHT_UNDEFINED:
    Constant for uiMode: a UI_MODE_NIGHT_MASK
    value indicating that no mode type has been set. 
    """
    UI_MODE_NIGHT_UNDEFINED = 0x00000000

    """
    public static final int UI_MODE_NIGHT_YES:
    Constant for uiMode: a UI_MODE_NIGHT_MASK
    value that corresponds to the
    night
    resource qualifier. 
    """
    UI_MODE_NIGHT_YES = 0x00000020

    """
    public static final int UI_MODE_TYPE_APPLIANCE:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to the
    appliance
    resource qualifier. 
    """
    UI_MODE_TYPE_APPLIANCE = 0x00000005

    """
    public static final int UI_MODE_TYPE_CAR:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to the
    car
    resource qualifier. 
    """
    UI_MODE_TYPE_CAR = 0x00000003

    """
    public static final int UI_MODE_TYPE_DESK:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to the
    desk
    resource qualifier. 
    """
    UI_MODE_TYPE_DESK = 0x00000002

    """
    public static final int UI_MODE_TYPE_MASK:
    Constant for uiMode: bits that encode the mode type. 
    """
    UI_MODE_TYPE_MASK = 0x0000000f

    """
    public static final int UI_MODE_TYPE_NORMAL:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to
    no
    UI mode resource qualifier specified. 
    """
    UI_MODE_TYPE_NORMAL = 0x00000001

    """
    public static final int UI_MODE_TYPE_TELEVISION:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to the
    television
    resource qualifier. 
    """
    UI_MODE_TYPE_TELEVISION = 0x00000004

    """
    public static final int UI_MODE_TYPE_UNDEFINED:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value indicating that no mode type has been set. 
    """
    UI_MODE_TYPE_UNDEFINED = 0x00000000

    """
    public static final int UI_MODE_TYPE_VR_HEADSET:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to the
    vrheadset
    resource qualifier. 
    """
    UI_MODE_TYPE_VR_HEADSET = 0x00000007

    """
    public static final int UI_MODE_TYPE_WATCH:
    Constant for uiMode: a UI_MODE_TYPE_MASK
    value that corresponds to the
    watch
    resource qualifier. 
    """
    UI_MODE_TYPE_WATCH = 0x00000006

    """
    public static final Creator<Configuration> CREATOR:
    
    """
    CREATOR = type(
        'ConfigurationCreator',
        (IParcelable.ICreator,),
        {
            'createFromParcel': lambda self, inparcel: reduce(
                lambda t, x: t.readFromParcel(x) or t, [inparcel], Configuration()
            ),
            'newArray': lambda self, size: (size * Configuration)()
        }
    )()

    @overload
    def __init__(self):
        super(Configuration, self).__init__()
        """
        public int colorMode:
        Bit mask of color capabilities of the screen. Currently there are two 
        fields:
        The COLOR_MODE_WIDE_COLOR_GAMUT_MASK bits define the color gamut of
        the screen. They may be one of
        COLOR_MODE_WIDE_COLOR_GAMUT_NO or COLOR_MODE_WIDE_COLOR_GAMUT_YES.The 
        COLOR_MODE_HDR_MASK defines the dynamic range of the screen. They may be
        one of COLOR_MODE_HDR_NO or COLOR_MODE_HDR_YES.See Supporting
        Multiple Screens for more information.
        """
        self.colorMode = None

        """
        public int densityDpi:
        The target screen density being rendered to, corresponding to density
        resource qualifier.  Set to DENSITY_DPI_UNDEFINED if no density is specified.
        """
        self.densityDpi = None

        """
        public float fontScale:
        Current user preference for the scaling factor for fonts, relative
        to the base density scaling.
        """
        self.fontScale = None

        """
        public int hardKeyboardHidden:
        A flag indicating whether the hard keyboard has been hidden.  This will
        be set on a device with a mechanism to hide the keyboard from the
        user, when that mechanism is closed.  One of:
        HARDKEYBOARDHIDDEN_NO, HARDKEYBOARDHIDDEN_YES.
        """
        self.hardKeyboardHidden = None

        """
        public int keyboard:
        The kind of keyboard attached to the device.
        One of: KEYBOARD_NOKEYS, KEYBOARD_QWERTY, KEYBOARD_12KEY.
        """
        self.keyboard = None

        """
        public int keyboardHidden:
        A flag indicating whether any keyboard is available.  Unlike
        hardKeyboardHidden, this also takes into account a soft
        keyboard, so if the hard keyboard is hidden but there is soft
        keyboard available, it will be set to NO.  Value is one of:
        KEYBOARDHIDDEN_NO, KEYBOARDHIDDEN_YES.
        """
        self.keyboardHidden = None

        """
        public Locale locale:

        This field was deprecated
        in API level 24.
        Do not set or read this directly. Use getLocales() and
        setLocales(LocaleList). If only the primary locale is needed,
        getLocales().get(0) is now the preferred accessor.

        Current user preference for the locale, corresponding to
        locale resource qualifier.
        """
        self.locale = None

        """
        public int mcc:
        IMSI MCC (Mobile Country Code), corresponding to mcc resource qualifier.  
        0 if undefined.
        """
        self.mcc = None

        """
        public int mnc:
        IMSI MNC (Mobile Network Code), corresponding to
        mnc
        resource qualifier.  0 if undefined. Note that the actual MNC may be 0; in 
        order to check
        for this use the MNC_ZERO symbol.
        """
        self.mnc = None

        """
        public int navigation:
        The kind of navigation method available on the device.
        One of: NAVIGATION_NONAV, NAVIGATION_DPAD,
        NAVIGATION_TRACKBALL, NAVIGATION_WHEEL.
        """
        self.navigation = None

        """
        public int navigationHidden:
        A flag indicating whether any 5-way or DPAD navigation available.
        This will be set on a device with a mechanism to hide the navigation
        controls from the user, when that mechanism is closed.  One of:
        NAVIGATIONHIDDEN_NO, NAVIGATIONHIDDEN_YES.
        """
        self.navigationHidden = None

        """
        public int orientation:
        Overall orientation of the screen.  May be one of
        ORIENTATION_LANDSCAPE, ORIENTATION_PORTRAIT.
        """
        self.orientation = None

        """
        public int screenHeightDp:
        The current height of the available screen space, in dp units,
        corresponding to
        screen
        height resource qualifier.  Set to
        SCREEN_HEIGHT_DP_UNDEFINED if no height is specified.
        """
        self.screenHeightDp = None

        """
        public int screenLayout:
        Bit mask of overall layout of the screen.  Currently there are four
        fields:
        The SCREENLAYOUT_SIZE_MASK bits define the overall size
        of the screen.  They may be one of
        SCREENLAYOUT_SIZE_SMALL, SCREENLAYOUT_SIZE_NORMAL,
        SCREENLAYOUT_SIZE_LARGE, or SCREENLAYOUT_SIZE_XLARGE.The 
        SCREENLAYOUT_LONG_MASK defines whether the screen
        is wider/taller than normal.  They may be one of
        SCREENLAYOUT_LONG_NO or SCREENLAYOUT_LONG_YES.The 
        SCREENLAYOUT_LAYOUTDIR_MASK defines whether the screen layout
        is either LTR or RTL.  They may be one of
        SCREENLAYOUT_LAYOUTDIR_LTR or SCREENLAYOUT_LAYOUTDIR_RTL.The 
        SCREENLAYOUT_ROUND_MASK defines whether the screen has a rounded
        shape. They may be one of SCREENLAYOUT_ROUND_NO or SCREENLAYOUT_ROUND_YES.
        See Supporting
        Multiple Screens for more information.
        """
        self.screenLayout = None

        """
        public int screenWidthDp:
        The current width of the available screen space, in dp units, corresponding 
        to screen width resource qualifier.  Set to SCREEN_WIDTH_DP_UNDEFINED if no 
        width is specified.
        """
        self.screenWidthDp = None

        """
        public int smallestScreenWidthDp:
        The smallest screen size an application will see in normal operation,
        corresponding to smallest screen width resource qualifier.
        This is the smallest value of both screenWidthDp and screenHeightDp
        in both portrait and landscape.  Set to SMALLEST_SCREEN_WIDTH_DP_UNDEFINED 
        if no width is specified.
        """
        self.smallestScreenWidthDp = None

        """
        public int touchscreen:
        The kind of touch screen attached to the device.
        One of: TOUCHSCREEN_NOTOUCH, TOUCHSCREEN_FINGER.
        """
        self.touchscreen = None

        """
        public int uiMode:
        Bit mask of the ui mode.  Currently there are two fields:
        The UI_MODE_TYPE_MASK bits define the overall ui mode of the
        device. They may be one of UI_MODE_TYPE_UNDEFINED,
        UI_MODE_TYPE_NORMAL, UI_MODE_TYPE_DESK,
        UI_MODE_TYPE_CAR, UI_MODE_TYPE_TELEVISION,
        UI_MODE_TYPE_APPLIANCE, UI_MODE_TYPE_WATCH,
        or UI_MODE_TYPE_VR_HEADSET.

        The UI_MODE_NIGHT_MASK defines whether the screen
        is in a special mode. They may be one of UI_MODE_NIGHT_UNDEFINED,
        UI_MODE_NIGHT_NO or UI_MODE_NIGHT_YES.
        """
        self.uiMode = None

        self.setToDefaults()
        self.fontScale = 0.0
        pass

    @__init__.adddef('Configuration')
    def __init__(self, o):
        """
        :param o: Configuration.
        """
        super(Configuration, self).__init__()
        self.setTo(o)
        pass

    def compareTo(self, that):
        """
        :param that: Configuration
        :return: int.
        """
        this = self
        a = this.fontScale
        b = that.fontScale
        if a < b: return -1
        if a > b: return 1
        n = this.mcc - that.mcc
        if n != 0: return n
        n = this.mnc - that.mnc
        if n != 0: return n
        this.fixUpLocaleList()
        that.fixUpLocaleList()
        # for backward compatibility, we consider an empty locale list to be greater
        # than any non - empty locale list.
        if this.mLocaleList.isEmpty():
            if not that.mLocaleList.isEmpty(): return 1
            elif that.mLocaleList.isEmpty(): return -1
        else:
            minSize = min(this.mLocaleList.size(), that.mLocaleList.size())
            for i in range(minSize):
                thisLocale = this.mLocaleList.get(i)
                thatLocale = that.mLocaleList.get(i)
                n = thisLocale.getLanguage().compareTo(thatLocale.getLanguage())
                if n != 0: return n
                n = thisLocale.getCountry().compareTo(thatLocale.getCountry())
                if n != 0: return n
                n = thisLocale.getVariant().compareTo(thatLocale.getVariant())
                if n != 0: return n
                n = thisLocale.toLanguageTag().compareTo(thatLocale.toLanguageTag())
                if n != 0: return n
            n = this.mLocaleList.size() - that.mLocaleList.size()
            if n != 0: return n
        n = this.touchscreen - that.touchscreen
        if n != 0: return n
        n = this.keyboard - that.keyboard
        if n != 0: return n
        n = this.keyboardHidden - that.keyboardHidden
        if n != 0: return n
        n = this.hardKeyboardHidden - that.hardKeyboardHidden
        if n != 0: return n
        n = this.navigation - that.navigation
        if n != 0: return n
        n = this.navigationHidden - that.navigationHidden
        if n != 0: return n
        n = this.orientation - that.orientation
        if n != 0: return n
        n = this.colorMode - that.colorMode
        if n != 0: return n
        n = this.screenLayout - that.screenLayout
        if n != 0: return n
        n = this.uiMode - that.uiMode
        if n != 0: return n
        n = this.screenWidthDp - that.screenWidthDp
        if n != 0: return n
        n = this.screenHeightDp - that.screenHeightDp
        if n != 0: return n
        n = this.smallestScreenWidthDp - that.smallestScreenWidthDp
        if n != 0: return n
        n = this.densityDpi - that.densityDpi
        if n != 0: return n
        n = this.assetsSeq - that.assetsSeq
        if n != 0: return n
        n = this.windowConfiguration.compareTo(that.windowConfiguration)
        if n != 0: return n
        return 0

    def describeContents(self):
        """
        Parcelable methods
        :return: int. a bitmask indicating the set of special object types 
        marshaled by this Parcelable object instance.
        """
        return 0

    def diff(self, delta):
        """
        Return a bit mask of the differences between this Configuration object 
        and the given one.  Does not change the values of either.  Any 
        undefined fields in delta are ignored.
        :param delta: Configuration
        :return: int. Returns a bit mask indicating which configuration values 
        has changed, containing any combination of 
        PackageManager.ActivityInfo.CONFIG_FONT_SCALE, 
        PackageManager.ActivityInfo.CONFIG_MCC, 
        PackageManager.ActivityInfo.CONFIG_MNC, 
        PackageManager.ActivityInfo.CONFIG_LOCALE, 
        PackageManager.ActivityInfo.CONFIG_TOUCHSCREEN, 
        PackageManager.ActivityInfo.CONFIG_KEYBOARD, 
        PackageManager.ActivityInfo.CONFIG_NAVIGATION, 
        PackageManager.ActivityInfo.CONFIG_ORIENTATION, 
        PackageManager.ActivityInfo.CONFIG_SCREEN_LAYOUT, or 
        PackageManager.ActivityInfo.CONFIG_SCREEN_SIZE, or 
        PackageManager.ActivityInfo.CONFIG_SMALLEST_SCREEN_SIZE. 
        PackageManager.ActivityInfo.CONFIG_LAYOUT_DIRECTION.
        """
        changed = 0
        if delta.fontScale > 0 and self.fontScale != delta.fontScale:
            changed |= ActivityInfo.CONFIG_FONT_SCALE
        if delta.mcc != 0 and self.mcc != delta.mcc:
            changed |= ActivityInfo.CONFIG_MCC
        if delta.mnc != 0 and self.mnc != delta.mnc:
            changed |= ActivityInfo.CONFIG_MNC
        self.fixLocaleList()
        delta.fixLocaleList()
        if not delta.mLocaleList.isEmpty() and not self.mLocaleList.equals(delta.mLocaleList):
            changed |= ActivityInfo.CONFIG_LOCALE
            changed |= ActivityInfo.CONFIG_LAYOUT_DIRECTION
        deltaScreenLayoutDir = delta.screenLayout & self.SCREENLAYOUT_LAYOUTDIR_MASK
        if deltaScreenLayoutDir != self.SCREENLAYOUT_LAYOUTDIR_UNDEFINED and \
                deltaScreenLayoutDir != (self.screenLayout & self.SCREENLAYOUT_LAYOUTDIR_MASK):
            changed |= ActivityInfo.CONFIG_LAYOUT_DIRECTION
        # if (delta.userSetLocale and (not self.userSetLocale or ((changed & ActivityInfo.CONFIG_LOCALE) != 0))):
        #     changed |= ActivityInfo.CONFIG_LOCALE
        if delta.touchscreen != self.TOUCHSCREEN_UNDEFINED and self.touchscreen != delta.touchscreen:
            changed |= ActivityInfo.CONFIG_TOUCHSCREEN
        if delta.keyboard != self.KEYBOARD_UNDEFINED and self.keyboard != delta.keyboard:
            changed |= ActivityInfo.CONFIG_KEYBOARD
        if delta.keyboardHidden != self.KEYBOARDHIDDEN_UNDEFINED and self.keyboardHidden != delta.keyboardHidden:
            changed |= ActivityInfo.CONFIG_KEYBOARD_HIDDEN
        if delta.hardKeyboardHidden != self.HARDKEYBOARDHIDDEN_UNDEFINED and self.hardKeyboardHidden != delta.hardKeyboardHidden:
            changed |= ActivityInfo.CONFIG_KEYBOARD_HIDDEN
        if delta.navigation != self.NAVIGATION_UNDEFINED and self.navigation != delta.navigation:
            changed |= ActivityInfo.CONFIG_NAVIGATION
        if delta.navigationHidden != self.NAVIGATIONHIDDEN_UNDEFINED and self.navigationHidden != delta.navigationHidden:
            changed |= ActivityInfo.CONFIG_KEYBOARD_HIDDEN
        if delta.orientation != self.ORIENTATION_UNDEFINED and self.orientation != delta.orientation:
            changed |= ActivityInfo.CONFIG_ORIENTATION
        dmy = self.SCREENLAYOUT_SIZE_MASK
        if (((delta.screenLayout & dmy) != self.SCREENLAYOUT_SIZE_UNDEFINED) \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
        dmy = self.SCREENLAYOUT_LONG_MASK
        if (((delta.screenLayout & dmy) != self.SCREENLAYOUT_LONG_UNDEFINED) \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
        dmy = self.SCREENLAYOUT_ROUND_MASK
        if (((delta.screenLayout & dmy) != self.SCREENLAYOUT_ROUND_UNDEFINED) \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
        dmy = self.SCREENLAYOUT_COMPAT_NEEDED
        if (delta.screenLayout != 0 \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
        dmy = self.COLOR_MODE_WIDE_COLOR_GAMUT_MASK
        if (((delta.colormode & dmy) != self.COLOR_MODE_WIDE_COLOR_GAMUT_UNDEFINED) \
                and (delta.colormode & dmy) != (self.colormode & dmy)):
            changed |= ActivityInfo.CONFIG_COLOR_MODE
        dmy = self.COLOR_MODE_HDR_MASK
        if (((delta.colormode & dmy) != self.COLOR_MODE_HDR_UNDEFINED) \
                and (delta.colormode & dmy) != (self.colormode & dmy)):
            changed |= ActivityInfo.CONFIG_COLOR_MODE
        if (delta.uiMode != (self.UI_MODE_TYPE_UNDEFINED | self.UI_MODE_NIGHT_UNDEFINED)) \
                and (delta.uiMode != self.uiMode):
            changed |= ActivityInfo.CONFIG_UI_MODE
        if (delta.screenWidthDp != self.SCREEN_WIDTH_DP_UNDEFINED \
                and self.screenWidthDp != delta.screenWidthDp):
            changed |= ActivityInfo.CONFIG_SCREEN_SIZE
        if (delta.screenHeightDp != self.SCREEN_HEIGHT_DP_UNDEFINED \
                and self.screenHeightDp != delta.screenHeightDp):
            changed |= ActivityInfo.CONFIG_SCREEN_SIZE
        if (delta.smallestScreenWidthDp != self.SMALLEST_SCREEN_WIDTH_DP_UNDEFINED \
                and self.smallestScreenWidthDp != delta.smallestScreenWidthDp):
            changed |= ActivityInfo.CONFIG_SMALLEST_SCREEN_SIZE
        if (delta.densityDpi != self.DENSITY_DPI_UNDEFINED \
                and self.densityDpi != delta.densityDpi):
            changed |= ActivityInfo.CONFIG_DENSITY
        if delta.assetsSeq != self.ASSETS_SEQ_UNDEFINED and self.assetsSeq != delta.assetsSeq:
            changed |= ActivityInfo.CONFIG_ASSETS_PATHS
        if delta.seq != 0:
            self.seq = delta.seq
        if self.windowConfiguration.diff(delta.windowConfiguration) != 0:
            changed |= ActivityInfo.CONFIG_WINDOW_CONFIGURATION
        return changed

    @overload('Configuration')
    def equals(self, that):
        """
        :param that: Configuration
        :return: boolean.
        """
        this = self
        if that == None: return False
        if id(that) == id(this): return True
        return this.compareTo(that)== 0

    @equals.adddef('Object')
    def equals(self, that):
        """
        Indicates whether some other object is "equal to" this one.  The 
        equals method implements an equivalence relation on non-null object 
        references: It is reflexive: for any non-null reference value x, 
        x.equals(x) should return true. It is symmetric: for any non-null 
        reference values x and y, x.equals(y) should return true if and only 
        if y.equals(x) returns true. It is transitive: for any non-null 
        reference values x, y, and z, if x.equals(y) returns true and 
        y.equals(z) returns true, then x.equals(z) should return true. It is 
        consistent: for any non-null reference values x and y, multiple 
        invocations of x.equals(y) consistently return true or consistently 
        return false, provided no information used in equals comparisons on 
        the objects is modified. For any non-null reference value x, 
        x.equals(null) should return false.  The equals method for class 
        Object implements the most discriminating possible equivalence 
        relation on objects; that is, for any non-null reference values x and 
        y, this method returns true if and only if x and y refer to the same 
        object (x == y has the value true).  Note that it is generally 
        necessary to override the hashCode method whenever this method is 
        overridden, so as to maintain the general contract for the hashCode 
        method, which states that equal objects must have equal hash codes.
        :param that: Object: the reference object with which to compare.
        :return: boolean. true if this object is the same as the obj argument; 
        false otherwise.
        """
        # Overload always test instance
        # if isinstance(that, Configuration):
        #     return self.equals(that)
        return False

    def getLayoutDirection(self):
        """
        Return the layout direction. Will be either View.LAYOUT_DIRECTION_LTR 
        or View.LAYOUT_DIRECTION_RTL.
        :return: int. Returns View.LAYOUT_DIRECTION_RTL if the configuration 
        is SCREENLAYOUT_LAYOUTDIR_RTL, otherwise View.LAYOUT_DIRECTION_LTR.
        """
        bFlag = (self.screenLayout & self.SCREENLAYOUT_LAYOUTDIR_MASK) == self.SCREENLAYOUT_LAYOUTDIR_RTL
        # TODO: Una vez ported view a python cambiar por la instruccion que sigue
        # return View.LAYOUT_DIRECTION_RTL if bFlag else View.LAYOUT_DIRECTION_LTR
        return 0x00000001 if bFlag else 0x00000000

    def getLocales(self):
        """
        Get the locale list. This is the preferred way for getting the locales 
        (instead of using the direct accessor to locale, which would only 
        provide the primary locale).
        :return: LocaleList. The locale list. This value will never be null.
        """
        self.fixUpLocaleList()
        return self.mLocaleList

    def hashCode(self):
        """
        Returns a hash code value for the object. This method is supported for 
        the benefit of hash tables such as those provided by HashMap.  The 
        general contract of hashCode is: Whenever it is invoked on the same 
        object more than once during an execution of a Java application, the 
        hashCode method must consistently return the same integer, provided no 
        information used in equals comparisons on the object is modified. This 
        integer need not remain consistent from one execution of an 
        application to another execution of the same application. If two 
        objects are equal according to the equals(Object) method, then calling 
        the hashCode method on each of the two objects must produce the same 
        integer result. It is not required that if two objects are unequal 
        according to the equals(java.lang.Object) method, then calling the 
        hashCode method on each of the two objects must produce distinct 
        integer results.  However, the programmer should be aware that 
        producing distinct integer results for unequal objects may improve the 
        performance of hash tables.  As much as is reasonably practical, the 
        hashCode method defined by class Object does return distinct integers 
        for distinct objects. (This is typically implemented by converting the 
        internal address of the object into an integer, but this 
        implementation technique is not required by the Java&trade; 
        programming language.)
        :return: int. a hash code value for this object.
        """
        result = 17
        result = 31 * result + self.fontScale.__hash__()
        result = 31 * result + self.self.mcc
        result = 31 * result + self.mnc
        result = 31 * result + self.mLocaleList.hashCode()
        result = 31 * result + self.touchscreen
        result = 31 * result + self.keyboard
        result = 31 * result + self.keyboardHidden
        result = 31 * result + self.hardKeyboardHidden
        result = 31 * result + self.navigation
        result = 31 * result + self.navigationHidden
        result = 31 * result + self.orientation
        result = 31 * result + self.screenLayout
        result = 31 * result + self.colorMode
        result = 31 * result + self.uiMode
        result = 31 * result + self.screenWidthDp
        result = 31 * result + self.screenHeightDp
        result = 31 * result + self.smallestScreenWidthDp
        result = 31 * result + self.densityDpi
        result = 31 * result + self.assetsSeq
        return result

    def isLayoutSizeAtLeast(self, size):
        """
        Check if the Configuration's current screenLayout is at least the 
        given size.
        :param size: int: The desired size, either SCREENLAYOUT_SIZE_SMALL, 
        SCREENLAYOUT_SIZE_NORMAL, SCREENLAYOUT_SIZE_LARGE, or 
        SCREENLAYOUT_SIZE_XLARGE.
        :return: boolean. Returns true if the current screen layout size is at 
        least the given size.
        """
        cur = self.screenLayout & self.SCREENLAYOUT_SIZE_MASK
        if cur == self.SCREENLAYOUT_SIZE_UNDEFINED: return False
        return cur >= size

    def isScreenHdr(self):
        """
        Return whether the screen has a high dynamic range.
        :return: boolean. true if the screen has a high dynamic range, false 
        otherwise
        """
        return (self.colorMode & self.COLOR_MODE_HDR_MASK) == self.COLOR_MODE_HDR_YES

    def isScreenRound(self):
        """
        Return whether the screen has a round shape. Apps may choose to change 
        styling based on this property, such as the alignment or layout of 
        text or informational icons.
        :return: boolean. true if the screen is rounded, false otherwise
        """
        return (self.screenLayout & self.SCREENLAYOUT_ROUND_MASK) == self.SCREENLAYOUT_ROUND_YES

    def isScreenWideColorGamut(self):
        """
        Return whether the screen has a wide color gamut and wide color gamut 
        rendering is supported by this device.  When true, it implies the 
        screen is colorspace aware but not necessarily color-managed. The 
        final colors may still be changed by the screen depending on user 
        settings.
        :return: boolean. true if the screen has a wide color gamut and wide 
        color gamut rendering is supported, false otherwise
        """
        return (self.colorMode & self.COLOR_MODE_WIDE_COLOR_GAMUT_MASK) == self.COLOR_MODE_WIDE_COLOR_GAMUT_YES

    @classmethod
    def needNewResources(self, configChanges, interestingChanges):
        """
        Determines if a new resource needs to be loaded from the bit set of 
        configuration changes returned by updateFrom(Configuration).
        :param configChanges: int: the mask of changes configurations as 
        returned by updateFrom(Configuration)Value is either 0 or combination 
        of CONFIG_MCC, CONFIG_MNC, CONFIG_LOCALE, CONFIG_TOUCHSCREEN, 
        CONFIG_KEYBOARD, CONFIG_KEYBOARD_HIDDEN, CONFIG_NAVIGATION, 
        CONFIG_ORIENTATION, CONFIG_SCREEN_LAYOUT, CONFIG_UI_MODE, 
        CONFIG_SCREEN_SIZE, CONFIG_SMALLEST_SCREEN_SIZE, CONFIG_DENSITY, 
        CONFIG_LAYOUT_DIRECTION, CONFIG_COLOR_MODE or CONFIG_FONT_SCALE.
        :param interestingChanges: int: the configuration changes that the 
        resource can handle as given in TypedValue.changingConfigurationsValue 
        is either 0 or combination of CONFIG_MCC, CONFIG_MNC, CONFIG_LOCALE, 
        CONFIG_TOUCHSCREEN, CONFIG_KEYBOARD, CONFIG_KEYBOARD_HIDDEN, 
        CONFIG_NAVIGATION, CONFIG_ORIENTATION, CONFIG_SCREEN_LAYOUT, 
        CONFIG_UI_MODE, CONFIG_SCREEN_SIZE, CONFIG_SMALLEST_SCREEN_SIZE, 
        CONFIG_DENSITY, CONFIG_LAYOUT_DIRECTION, CONFIG_COLOR_MODE or 
        CONFIG_FONT_SCALE.
        :return: boolean. true if the resource needs to be loaded, false 
        otherwise
        """
        interestingChanges = interestingChanges | \
                             ActivityInfo.CONFIG_ASSETS_PATHS | \
                             ActivityInfo.CONFIG_FONT_SCALE
        return (configChanges & interestingChanges) != 0

    def readFromParcel(self, source):
        """
        :param source: Parcel
        """
        self.fontScale = source.readFloat()
        self.mcc = source.readInt()
        self.mnc = source.readInt()
        self.mLocaleList = source.readParcelable(LocaleList.getClassLoader())
        self.locale = self.mLocaleList.get(0)
        self.userSetLocale = (source.readInt() == 1)
        self.touchscreen = source.readInt()
        self.keyboard = source.readInt()
        self.keyboardHidden = source.readInt()
        self.hardKeyboardHidden = source.readInt()
        self.navigation = source.readInt()
        self.navigationHidden = source.readInt()
        self.orientation = source.readInt()
        self.screenLayout = source.readInt()
        self.colorMode = source.readInt()
        self.uiMode = source.readInt()
        self.screenWidthDp = source.readInt()
        self.screenHeightDp = source.readInt()
        self.smallestScreenWidthDp = source.readInt()
        self.densityDpi = source.readInt()
        self.compatScreenWidthDp = source.readInt()
        self.compatScreenHeightDp = source.readInt()
        self.compatSmallestScreenWidthDp = source.readInt()
        self.windowConfiguration.setTo(source.readValue(None))
        self.assetsSeq = source.readInt()
        self.seq = source.readInt()
        pass

    def setLayoutDirection(self, loc):
        """
        Set the layout direction from a Locale.
        :param loc: Locale: The Locale. If null will set the layout direction 
        to View.LAYOUT_DIRECTION_LTR. If not null will set it to the layout 
        direction corresponding to the Locale.
        See also:
        View.LAYOUT_DIRECTION_LTR = 0x00000000
        View.LAYOUT_DIRECTION_RTL = 0x00000001
        """
        layoutDirection = 1 + 0x00000000        # 1 + View.LAYOUT_DIRECTION_LTR
        self.screenLayout = (self.screenLayout & ~self.SCREENLAYOUT_LAYOUTDIR_MASK) | \
                       (layoutDirection << self.SCREENLAYOUT_LAYOUTDIR_SHIFT)
        pass

    def setLocale(self, loc):
        """
        Set the locale list to a list of just one locale. This will also set 
        the layout direction according to the locale.  Note that after this is 
        run, calling .equals() on the input locale and the locale attribute 
        would return true if they are not null, but there is no guarantee that 
        they would be the same object.  See also the note about layout 
        direction in setLocales(LocaleList).
        :param loc: Locale: The locale. Can be null.
        """
        self.setLocales(LocaleList.getEmptyLocaleList() if loc == None else LocaleList(loc))

    def setLocales(self, locales):
        """
        Set the locale list. This is the preferred way for setting up the 
        locales (instead of using the direct accessor or setLocale(Locale)). 
        This will also set the layout direction according to the first locale 
        in the list.  Note that the layout direction will always come from the 
        first locale in the locale list, even if the locale is not supported 
        by the resources (the resources may only support another locale 
        further down the list which has a different direction).
        :param locales: LocaleList: The locale list. If null, an empty 
        LocaleList will be assigned.
        """
        self.mLocaleList = LocaleList.getEmptyLocaleList() if locales == None else locales
        self.locale = self.mLocaleList.get(0)
        self.setLayoutDirection(self.locale)
        pass

    def setTo(self, o):
        """
        Sets the fields in this object to those in the given Configuration.
        :param o: Configuration: The Configuration object used to set the 
        values of this Configuration's fields.
        """
        self.fontScale = o.fontScale
        self.mcc = o.mcc
        self.mnc = o.mnc
        self.locale = None if o.locale is None else o.locale.clone()
        o.fixUpLocaleList()
        self.mLocaleList = o.mLocaleList
        self.userSetLocale = o.userSetLocale
        self.touchscreen = o.touchscreen
        self.keyboard = o.keyboard
        self.keyboardHidden = o.keyboardHidden
        self.hardKeyboardHidden = o.hardKeyboardHidden
        self.navigation = o.navigation
        self.navigationHidden = o.navigationHidden
        self.orientation = o.orientation
        self.screenLayout = o.screenLayout
        self.colorMode = o.colorMode
        self.uiMode = o.uiMode
        self.screenWidthDp = o.screenWidthDp
        self.screenHeightDp = o.screenHeightDp
        self.smallestScreenWidthDp = o.smallestScreenWidthDp
        self.densityDpi = o.densityDpi
        self.compatScreenWidthDp = o.compatScreenWidthDp
        self.compatScreenHeightDp = o.compatScreenHeightDp
        self.compatSmallestScreenWidthDp = o.compatSmallestScreenWidthDp
        self.assetsSeq = o.assetsSeq
        self.seq = o.seq
        self.windowConfiguration.setTo(o.windowConfiguration)
        pass

    def setToDefaults(self):
        """
        Set this object to the system defaults.
        """
        self.colorMode = self.COLOR_MODE_UNDEFINED
        self.densityDpi = self.DENSITY_DPI_UNDEFINED
        self.fontScale = 1
        self.hardKeyboardHidden = self.HARDKEYBOARDHIDDEN_UNDEFINED
        self.keyboard = self.KEYBOARD_UNDEFINED
        self.keyboardHidden = self.KEYBOARDHIDDEN_UNDEFINED
        self.locale = None
        self.mcc = self.mnc = 0
        self.mLocaleList = LocaleList.getEmptyLocaleList()
        self.navigation = self.NAVIGATION_UNDEFINED
        self.navigationHidden = self.NAVIGATIONHIDDEN_UNDEFINED
        self.orientation = self.ORIENTATION_UNDEFINED
        self.screenHeightDp = self.compatScreenHeightDp = self.SCREEN_HEIGHT_DP_UNDEFINED
        self.screenLayout = self.SCREENLAYOUT_UNDEFINED
        self.screenWidthDp = self.compatScreenWidthDp = self.SCREEN_WIDTH_DP_UNDEFINED
        self.smallestScreenWidthDp = self.compatSmallestScreenWidthDp = self.SMALLEST_SCREEN_WIDTH_DP_UNDEFINED
        self.touchscreen = self.TOUCHSCREEN_UNDEFINED
        self.uiMode = self.UI_MODE_TYPE_UNDEFINED
        self.userSetLocale = False
        self.assetsSeq = self.ASSETS_SEQ_UNDEFINED
        self.seq = 0
        self.windowConfiguration.setToDefaults()
        pass

    def toString(self):
        """
        Returns a string representation of the object. In general, the 
        toString method returns a string that "textually represents" this 
        object. The result should be a concise but informative representation 
        that is easy for a person to read. It is recommended that all 
        subclasses override this method.  The toString method for class Object 
        returns a string consisting of the name of the class of which the 
        object is an instance, the at-sign character `@', and the unsigned 
        hexadecimal representation of the hash code of the object. In other 
        words, this method returns a string equal to the value of:  
        getClass().getName() + '@' + Integer.toHexString(hashCode())
        :return: String. a string representation of the object.
        """
        sb = str(self.fontScale) + ' '
        sb += (str(self.mcc) if self.mcc else '?') + 'mcc'
        sb += (str(self.mnc) if self.mnc else '?') + 'mnc'
        self.fixUpLocaleList()
        if not self.mLocaleList.isEmpty():
            sb += ' ' + str(self.mLocaleList)
        else:
            sb += ' ?localeList'
        layoutDir = self.screenLayout & self.SCREENLAYOUT_LAYOUTDIR_MASK
        if layoutDir == self.SCREENLAYOUT_LAYOUTDIR_UNDEFINED: sb += ' ?layoutDir'
        elif layoutDir == self.SCREENLAYOUT_LAYOUTDIR_LTR: sb += ' ldltr'
        elif layoutDir == self.SCREENLAYOUT_LAYOUTDIR_RTL: sb += ' ldrtl'
        else: sb += ' layoutDir=' + str(self.layoutDir >> self.SCREENLAYOUT_LAYOUTDIR_SHIFT)
        sb += (' sw' + str(self.smallestScreenWidthDp) + 'dp') \
            if self.smallestScreenWidthDp != self.SMALLEST_SCREEN_WIDTH_DP_UNDEFINED else \
            ' ?swdp'
        sb += (' w' + str(self.screenWidthDp) + 'dp') \
            if self.screenWidthDp != self.SCREEN_WIDTH_DP_UNDEFINED else \
            ' ?wdp'
        sb += (' h' + str(self.screenHeightDp) + 'dp') \
            if self.screenHeightDp != self.SCREEN_HEIGHT_DP_UNDEFINED else \
            ' ?hdp'
        sb += (' ' + str(self.densityDpi) + 'dp') \
            if self.densityDpi != self.DENSITY_DPI_UNDEFINED else \
            ' ?density'
        layoutDir = self.screenLayout & self.SCREENLAYOUT_SIZE_MASK
        if layoutDir == self.SCREENLAYOUT_SIZE_UNDEFINED: sb += ' ?lsize'
        elif layoutDir == self.SCREENLAYOUT_SIZE_SMALL: sb += ' smll'
        elif layoutDir == self.SCREENLAYOUT_SIZE_NORMAL: sb += ' nrml'
        elif layoutDir == self.SCREENLAYOUT_SIZE_LARGE: sb += ' lrg'
        elif layoutDir == self.SCREENLAYOUT_SIZE_XLARGE: sb += ' xlrg'
        else: sb += ' layoutSize=' + str(layoutDir)
        layoutDir = self.screenLayout & self.SCREENLAYOUT_LONG_MASK
        if layoutDir == self.SCREENLAYOUT_LONG_UNDEFINED: sb += ' ?long'
        elif layoutDir == self.SCREENLAYOUT_LONG_NO: pass
        elif layoutDir == self.SCREENLAYOUT_LONG_YES: sb += ' long'
        else: sb += ' layoutLong=' + str(layoutDir)
        layoutDir = self.colorMode & self.COLOR_MODE_HDR_MASK
        if layoutDir == self.COLOR_MODE_HDR_UNDEFINED: sb += ' ?ldr'
        elif layoutDir == self.COLOR_MODE_HDR_NO: pass
        elif layoutDir == self.COLOR_MODE_HDR_YES: sb += ' hdr'
        else: sb += ' dynamicRange=' + str(layoutDir)
        layoutDir = self.colorMode & self.COLOR_MODE_WIDE_COLOR_GAMUT_MASK
        if layoutDir == self.COLOR_MODE_WIDE_COLOR_GAMUT_UNDEFINED: sb += ' ?wideColorGamut'
        elif layoutDir == self.COLOR_MODE_WIDE_COLOR_GAMUT_NO: pass
        elif layoutDir == self.COLOR_MODE_WIDE_COLOR_GAMUT_YES: sb += ' widecg'
        else: sb += ' wideColorGamut=' + str(layoutDir)
        layoutDir = self.orientation
        if layoutDir == self.ORIENTATION_UNDEFINED: sb += ' ?orien'
        elif layoutDir == self.ORIENTATION_LANDSCAPE: sb += ' land'
        elif layoutDir == self.ORIENTATION_PORTRAIT: sb += ' port'
        else: sb += ' orien=' + str(layoutDir)
        layoutDir = self.uiMode & self.UI_MODE_TYPE_MASK
        if layoutDir == self.UI_MODE_TYPE_UNDEFINED: sb += ' ?uimode'
        elif layoutDir == self.UI_MODE_TYPE_NORMAL: pass
        elif layoutDir == self.UI_MODE_TYPE_DESK: sb += ' desk'
        elif layoutDir == self.UI_MODE_TYPE_CAR: sb += ' car'
        elif layoutDir == self.UI_MODE_TYPE_TELEVISION: sb += ' television'
        elif layoutDir == self.UI_MODE_TYPE_APPLIANCE: sb += ' appliance'
        elif layoutDir == self.UI_MODE_TYPE_WATCH: sb += ' watch'
        elif layoutDir == self.UI_MODE_TYPE_VR_HEADSET: sb += ' vrheadset'
        else: sb += ' uimode=' + str(layoutDir)
        layoutDir = self.uiMode & self.UI_MODE_NIGHT_MASK
        if layoutDir == self.UI_MODE_NIGHT_UNDEFINED: sb += ' ?night'
        elif layoutDir == self.UI_MODE_NIGHT_NO: pass
        elif layoutDir == self.UI_MODE_NIGHT_YES: sb += ' night'
        else: sb += ' night=' + str(layoutDir)
        layoutDir = self.touchscreen
        if layoutDir == self.TOUCHSCREEN_UNDEFINED: sb += ' ?touch'
        elif layoutDir == self.TOUCHSCREEN_NOTOUCH: sb += ' -touch'
        elif layoutDir == self.TOUCHSCREEN_STYLUS: sb += ' stylus'
        elif layoutDir == self.TOUCHSCREEN_FINGER: sb += ' finger'
        else: sb += ' touch=' + str(layoutDir)
        layoutDir = self.keyboard
        if layoutDir == self.KEYBOARD_UNDEFINED: sb += ' ?keyb'
        elif layoutDir == self.KEYBOARD_NOKEYS: sb += ' -keyb'
        elif layoutDir == self.KEYBOARD_QWERTY: sb += ' qwerty'
        elif layoutDir == self.KEYBOARD_12KEY: sb += ' 12key'
        else: sb += ' keys=' + str(layoutDir)
        layoutDir = self.keyboardHidden
        if layoutDir == self.KEYBOARDHIDDEN_UNDEFINED: sb += ' /?'
        elif layoutDir == self.KEYBOARDHIDDEN_NO: sb += ' /v'
        elif layoutDir == self.KEYBOARDHIDDEN_YES: sb += ' /h'
        elif layoutDir == self.KEYBOARDHIDDEN_SOFT: sb += ' /s'
        else: sb += '/' + str(layoutDir)
        layoutDir = self.hardKeyboardHidden
        if layoutDir == self.HARDKEYBOARDHIDDEN_UNDEFINED: sb += ' /?'
        elif layoutDir == self.HARDKEYBOARDHIDDEN_NO: sb += ' /v'
        elif layoutDir == self.HARDKEYBOARDHIDDEN_YES: sb += ' /h'
        else: sb += '/' + str(layoutDir)
        layoutDir = self.navigation
        if layoutDir == self.NAVIGATION_UNDEFINED: sb += ' ?nav'
        elif layoutDir == self.NAVIGATION_NONAV: sb += ' -nav'
        elif layoutDir == self.NAVIGATION_DPAD: sb += ' dpad'
        elif layoutDir == self.NAVIGATION_TRACKBALL: sb += ' tball'
        elif layoutDir == self.NAVIGATION_WHEEL: sb += ' wheel'
        else: sb += ' nav=' + str(layoutDir)
        layoutDir = self.navigationHiddention
        if layoutDir == self.NAVIGATIONHIDDEN_UNDEFINED: sb += '/?'
        elif layoutDir == self.NAVIGATIONHIDDEN_NO: sb += '/v'
        elif layoutDir == self.NAVIGATIONHIDDEN_YES: sb += '/h'
        else: sb += '/' + str(layoutDir)
        sb += ' winConfig=' + self.windowConfiguration.toString()
        if self.assetsSeq: sb += 'as.' + str(self.assetsSeq)
        if self.seg: sb += ' s.' + str(self.seq)
        return '{' + sb + '}'

    def updateFrom(self, delta):
        """
        Copies the fields from delta into this Configuration object, keeping 
        track of which ones have changed. Any undefined fields in delta are 
        ignored and not copied in to the current Configuration.
        :param delta: ConfigurationThis value must never be null.
        :return: int. a bit mask of the changed fields, as per 
        diff(Configuration). Value is either 0 or combination of CONFIG_MCC,
        CONFIG_MNC, CONFIG_LOCALE, CONFIG_TOUCHSCREEN, CONFIG_KEYBOARD, 
        CONFIG_KEYBOARD_HIDDEN, CONFIG_NAVIGATION, CONFIG_ORIENTATION, 
        CONFIG_SCREEN_LAYOUT, CONFIG_UI_MODE, CONFIG_SCREEN_SIZE, 
        CONFIG_SMALLEST_SCREEN_SIZE, CONFIG_DENSITY, CONFIG_LAYOUT_DIRECTION, 
        CONFIG_COLOR_MODE or CONFIG_FONT_SCALE.
        """
        changed = 0
        if delta.fontScale > 0 and self.fontScale != delta.fontScale:
            changed |= ActivityInfo.CONFIG_FONT_SCALE
            self.fontScale = delta.fontScale
        if delta.mcc != 0 and self.mcc != delta.mcc:
            changed |= ActivityInfo.CONFIG_MCC
            self.mcc = delta.mcc
        if delta.mnc != 0 and self.mnc != delta.mnc:
            changed |= ActivityInfo.CONFIG_MNC
            self.mnc = delta.mnc
        self.fixLocaleList()
        delta.fixLocaleList()
        if not delta.mLocaleList.isEmpty() and not self.mLocaleList.equals(delta.mLocaleList):
            changed |= ActivityInfo.CONFIG_LOCALE
            self.mLocaleList = delta.mLocaleList
            if not delta.locale.equals(self.locale):
                self.locale = delta.locale.clone()
                changed |= ActivityInfo.CONFIG_LAYOUT_DIRECTION
                self.setLayoutDirection(self.locale)
        deltaScreenLayoutDir = delta.screenLayout & self.SCREENLAYOUT_LAYOUTDIR_MASK
        if deltaScreenLayoutDir != self.SCREENLAYOUT_LAYOUTDIR_UNDEFINED and \
                deltaScreenLayoutDir != (self.screenLayout & self.SCREENLAYOUT_LAYOUTDIR_MASK):
            self.screenLayout = (self.screenLayout & ~self.SCREENLAYOUT_LAYOUTDIR_MASK) | deltaScreenLayoutDir
            changed |= ActivityInfo.CONFIG_LAYOUT_DIRECTION
        if (delta.userSetLocale and (not self.userSetLocale or ((changed & ActivityInfo.CONFIG_LOCALE) != 0))):
            changed |= ActivityInfo.CONFIG_LOCALE
            self.userSetLocale = True
        if delta.touchscreen != self.TOUCHSCREEN_UNDEFINED and self.touchscreen != delta.touchscreen:
            changed |= ActivityInfo.CONFIG_TOUCHSCREEN
            self.touchscreen = delta.touchscreen
        if delta.keyboard != self.KEYBOARD_UNDEFINED and self.keyboard != delta.keyboard:
            changed |= ActivityInfo.CONFIG_KEYBOARD
            self.keyboard = delta.keyboard
        if delta.keyboardHidden != self.KEYBOARDHIDDEN_UNDEFINED and self.keyboardHidden != delta.keyboardHidden:
            changed |= ActivityInfo.CONFIG_KEYBOARD_HIDDEN
            self.keyboardHidden = delta.keyboardHidden
        if delta.hardKeyboardHidden != self.HARDKEYBOARDHIDDEN_UNDEFINED and self.hardKeyboardHidden != delta.hardKeyboardHidden:
            changed |= ActivityInfo.CONFIG_KEYBOARD_HIDDEN
            self.hardKeyboardHidden = delta.hardKeyboardHidden
        if delta.navigation != self.NAVIGATION_UNDEFINED and self.navigation != delta.navigation:
            changed |= ActivityInfo.CONFIG_NAVIGATION
            self.navigation = delta.navigation
        if delta.navigationHidden != self.NAVIGATIONHIDDEN_UNDEFINED and self.navigationHidden != delta.navigationHidden:
            changed |= ActivityInfo.CONFIG_KEYBOARD_HIDDEN
            self.navigationHidden = delta.navigationHidden
        if delta.orientation != self.ORIENTATION_UNDEFINED and self.orientation != delta.orientation:
            changed |= ActivityInfo.CONFIG_ORIENTATION
            self.orientation = delta.orientation
        dmy = self.SCREENLAYOUT_SIZE_MASK
        if (((delta.screenLayout & dmy) != self.SCREENLAYOUT_SIZE_UNDEFINED) \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
            self.screenLayout = (self.screenLayout & ~dmy) | (delta.screenLayout & dmy)
        dmy = self.SCREENLAYOUT_LONG_MASK
        if (((delta.screenLayout & dmy) != self.SCREENLAYOUT_LONG_UNDEFINED) \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
            self.screenLayout = (self.screenLayout & ~dmy) | (delta.screenLayout & dmy)
        dmy = self.SCREENLAYOUT_ROUND_MASK
        if (((delta.screenLayout & dmy) != self.SCREENLAYOUT_ROUND_UNDEFINED) \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
            self.screenLayout = (self.screenLayout & ~dmy) | (delta.screenLayout & dmy)
        dmy = self.SCREENLAYOUT_COMPAT_NEEDED
        if (delta.screenLayout != 0 \
                and (delta.screenLayout & dmy) != (self.screenLayout & dmy)):
            changed |= ActivityInfo.CONFIG_SCREEN_LAYOUT
            self.screenLayout = (self.screenLayout & ~dmy) | (delta.screenLayout & dmy)
        dmy = self.COLOR_MODE_WIDE_COLOR_GAMUT_MASK
        if (((delta.colormode & dmy) != self.COLOR_MODE_WIDE_COLOR_GAMUT_UNDEFINED) \
                and (delta.colormode & dmy) != (self.colormode & dmy)):
            changed |= ActivityInfo.CONFIG_COLOR_MODE
            self.colormode = (self.colormode & ~dmy) | (delta.colormode & dmy)
        dmy = self.COLOR_MODE_HDR_MASK
        if (((delta.colormode & dmy) != self.COLOR_MODE_HDR_UNDEFINED) \
                and (delta.colormode & dmy) != (self.colormode & dmy)):
            changed |= ActivityInfo.CONFIG_COLOR_MODE
            self.colormode = (self.colormode & ~dmy) | (delta.colormode & dmy)
        if (delta.uiMode != (self.UI_MODE_TYPE_UNDEFINED | self.UI_MODE_NIGHT_UNDEFINED)) \
                and (delta.uiMode != self.uiMode):
            changed |= ActivityInfo.CONFIG_UI_MODE
            if ((delta.uiMode & self.UI_MODE_TYPE_MASK) != self.UI_MODE_TYPE_UNDEFINED):
                self.uiMode = (self.uiMode & ~self.UI_MODE_TYPE_MASK) \
                | (delta.uiMode & self.UI_MODE_TYPE_MASK)
            if ((delta.uiMode & self.UI_MODE_NIGHT_MASK) != self.UI_MODE_NIGHT_UNDEFINED):
                self.uiMode = (self.uiMode & ~self.UI_MODE_NIGHT_MASK) \
                | (delta.uiMode & self.UI_MODE_NIGHT_MASK)
        if (delta.screenWidthDp != self.SCREEN_WIDTH_DP_UNDEFINED \
                and self.screenWidthDp != delta.screenWidthDp):
            changed |= ActivityInfo.CONFIG_SCREEN_SIZE
            self.screenWidthDp = delta.screenWidthDp
        if (delta.screenHeightDp != self.SCREEN_HEIGHT_DP_UNDEFINED \
                and self.screenHeightDp != delta.screenHeightDp):
            changed |= ActivityInfo.CONFIG_SCREEN_SIZE
            self.screenHeightDp = delta.screenHeightDp
        if (delta.smallestScreenWidthDp != self.SMALLEST_SCREEN_WIDTH_DP_UNDEFINED \
                and self.smallestScreenWidthDp != delta.smallestScreenWidthDp):
            changed |= ActivityInfo.CONFIG_SMALLEST_SCREEN_SIZE
            self.smallestScreenWidthDp = delta.smallestScreenWidthDp
        if (delta.densityDpi != self.DENSITY_DPI_UNDEFINED \
                and self.densityDpi != delta.densityDpi):
            changed |= ActivityInfo.CONFIG_DENSITY
            self.densityDpi = delta.densityDpi
        if delta.compatScreenWidthDp != self.SCREEN_WIDTH_DP_UNDEFINED:
            self.compatScreenWidthDp = delta.compatScreenWidthDp
        if delta.compatScreenHeightDp != self.SCREEN_HEIGHT_DP_UNDEFINED:
            self.compatScreenHeightDp = delta.compatScreenHeightDp
        if delta.compatSmallestScreenWidthDp != self.SMALLEST_SCREEN_WIDTH_DP_UNDEFINED:
            self.compatSmallestScreenWidthDp = delta.compatSmallestScreenWidthDp
        if delta.assetsSeq != self.CONFIG_ASSETS_PATHS:
            self.assetsSeq = delta.assetsSeq
        if delta.seq != 0:
            self.seq = delta.seq
        if self.windowConfiguration.updateFrom(delta.windowConfiguration) != 0:
            changed |= ActivityInfo.CONFIG_WINDOW_CONFIGURATION
        return changed

    def writeToParcel(self, dest, flags):
        """
        Flatten this object in to a Parcel.
        :param dest: Parcel: The Parcel in which the object should be written.
        :param flags: int: Additional flags about how the object should be 
        written. May be 0 or Parcelable.PARCELABLE_WRITE_RETURN_VALUE.
        """
        dest.writeFloat(self.fontScale)
        dest.writeInt(self.mcc)
        dest.writeInt(self.mnc)
        self.fixUpLocaleList()
        dest.writeParcelable(self.mLocaleList, flags)
        dest.writeInt(1*self.userSetLocale)
        dest.writeInt(self.touchscreen)
        dest.writeInt(self.keyboard)
        dest.writeInt(self.keyboardHidden)
        dest.writeInt(self.hardKeyboardHidden)
        dest.writeInt(self.navigation)
        dest.writeInt(self.navigationHidden)
        dest.writeInt(self.orientation)
        dest.writeInt(self.screenLayout)
        dest.writeInt(self.colorMode)
        dest.writeInt(self.uiMode)
        dest.writeInt(self.screenWidthDp)
        dest.writeInt(self.screenHeightDp)
        dest.writeInt(self.smallestScreenWidthDp)
        dest.writeInt(self.densityDpi)
        dest.writeInt(self.compatScreenWidthDp)
        dest.writeInt(self.compatScreenHeightDp)
        dest.writeInt(self.compatSmallestScreenWidthDp)
        dest.writeValue(self.windowConfiguration)
        dest.writeInt(self.assetsSeq)
        dest.writeInt(self.seq)
        pass

    def fixUpLocaleList(self):
        if ((self.locale == None and not self.mLocaleList.isEmpty()) or \
                (self.locale != None and not self.locale.equals(self.mLocaleList.get(0)))):
            self.mLocaleList = LocaleList.getEmptyLocaleList() \
                if self.locale == None else \
                LocaleList(self.locale)