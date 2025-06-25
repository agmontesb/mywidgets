# -*- coding: utf-8 -*-
"""
https://developer.android.com/reference/android/content/res/AssetManager
ported from:
https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/content/res/AssetManager.java
"""
import copy
import threading

from Android import Object, overload
from Android.util.TypedValue import TypedValue


class ApkAssets(object):
    pass


class AssetManager(Object):
    """
    Provides access to an application's raw asset files; see Resources for the way
    most applications will want to retrieve their resource data. This class
    presents a lower-level API that allows you to open and read raw files that
    have been bundled with the application as a simple stream of bytes.
    """
    """
    public static final int ACCESS_BUFFER:
    Mode for open(String, int): Attempt to load contents into
    memory, for fast small reads.
    """
    ACCESS_BUFFER = 0x00000003

    """
    public static final int ACCESS_RANDOM:
    Mode for open(String, int): Read chunks, and seek forward and
    backward.
    """
    ACCESS_RANDOM = 0x00000001

    """
    public static final int ACCESS_STREAMING:
    Mode for open(String, int): Read sequentially, with an
    occasional forward seek.
    """
    ACCESS_STREAMING = 0x00000002

    """
    public static final int ACCESS_UNKNOWN:
    Mode for open(String, int): no specific information about how
    data will be accessed.
    """
    ACCESS_UNKNOWN = 0x00000000

    mObject = None
    sSync = threading.RLock()
    sThis = threading.RLock()

    FRAMEWORK_APK_PATH = 'Android/framework-res.apk'

    sSystem = None
    mApkAssets = None
    sSystemApkAssets = None
    sSystemApkAssetsSet = None
    mOpen = True

    class Builder(Object):
        def __init__(self):
            super(AssetManager.Builder, self).__init__()
            self.mUserApkAssets = []

        def addApkAssets(self, apkAssets):
            self.mUserApkAssets.append(apkAssets)
            return self

        def build(self):
            sysApkAssets = AssetManager.getSystem().getApkAssets()
            apkAssets = copy.copy(sysApkAssets)
            for asset in self.mUserApkAssets:
                if asset in apkAssets: continue
                apkAssets.append(asset)
            assetManager = AssetManager(False)
            assetManager.mApkAssets = apkAssets
            return assetManager

    @overload
    def __init__(self):
        self.assets = None
        with self.sSync:
            self.createSystemAssetsInZygoteLocked()
            assets = self.sSystemApkAssets
        self.mObject = threading.RLock()
        self.setApkAssets(assets, False)

    @__init__.adddef('bool')
    def __init__(self, sentinel):
        self.mObject = threading.RLock()

    @classmethod
    def createSystemAssetsInZygoteLocked(cls):
        if cls.sSystem: return
        try:
            apkAssets = [ApkAssets.loadFromPath(cls.FRAMEWORK_APK_PATH, True)]
            cls.loadStaticRuntimeOverlays(apkAssets)
            cls.sSystemApkAssetsSet = set(apkAssets)
            cls.sSystemApkAssets = apkAssets
            cls.sSystem = AssetManager(True)
            cls.sSystem.setApkAssets(cls.sSystemApkAssets)
        except Exception as e:
            raise Exception('IllegalStateException:"Failed to create system AssetManager"')

    @classmethod
    def loadStaticRuntimeOverlays(cls, outApkAssets):
        pass

    @classmethod
    def getSystem(cls):
        with cls.sSync:
            cls.createSystemAssetsInZygoteLocked()
            return cls.sSystem

    def getResourceValue(self, resId, densityDpi, outValue, resolveRefs):
        if outValue is None:
            raise Exception('outValue must be a TypedValue instance')
        cookie = nativeGetResourceValue(self.mObject, resId, densityDpi, outValue, resolveRefs)
        if cookie <= 0: return False
        if outValue.type == TypedValue.TYPE_STRING:
            outValue.string = self.mApkAssets[cookie - 1].getStringFromPool(outValue.data)
        return True

    def close(self):
        """
        Close this asset manager.
        """
        with self.sThis:
            if not self.mOpen: return
            self.mOpen = False

    def setApkAssets(self, apkAssets, invalidateCaches):
        newApkAssets = copy.copy(self.sSystemApkAssets)
        for asset in apkAssets:
            if asset in newApkAssets: continue
            newApkAssets.append(asset)
        with self.sThis:
            self.mApkAssets = newApkAssets
            if invalidateCaches:
                self.invalidateCachesLocked(-1)

    def invalidateCachesLocked(self, diff):
        pass

    def getApkAssets(self):
        with self.sThis:
            if self.mOpen:
                return self.mApkAssets
        return []

    def findCookieForPath(self, path):
        with self.sThis:
            for k, asset in enumerate(self.mApkAssets):
                if path == asset.getAssetPath():
                    return k + 1
        return 0


    def getLocales(self):
        """
        Get the locales that this asset manager contains data for.  On SDK 21 
        (Android 5.0: Lollipop) and above, Locale strings are valid BCP-47 
        language tags and can be parsed using Locale.forLanguageTag(String).  
        On SDK 20 (Android 4.4W: Kitkat for watches) and below, locale strings 
        are of the form ll_CC where ll is a two letter language code, and CC 
        is a two letter country code.
        :return: String[].
        """
        pass

    def list(self, path):
        """
        Return a String array of all the assets at the given path.
        :param path: String: A relative path within the assets, i.e., 
        "docs/home.html".This value must never be null.
        :return: String[]. String[] Array of strings, one for each asset.  
        These file names are relative to 'path'.  You can open the file by 
        concatenating 'path' and a name in the returned string (via File) and 
        passing that to open().This value may be null.
        :raises: IOException
        See also: open(String)
        """
        pass

    @overload('str', 'int')
    def open(self, fileName, accessMode):
        """
        Open an asset using an explicit access mode, returning an InputStream 
        to read its contents.  This provides access to files that have been 
        bundled with an application as assets -- that is, files placed in to 
        the "assets" directory.
        :param fileName: String: The name of the asset to open.  This name can 
        be hierarchical.This value must never be null.
        :param accessMode: int: Desired access mode for retrieving the data.
        :return: InputStream. This value will never be null.
        :raises: IOException
        See also:
        ACCESS_UNKNOWN
        ACCESS_STREAMING
        ACCESS_RANDOM
        ACCESS_BUFFER
        open(String)
        list(String)
        """
        pass

    @open.adddef('str')
    def open(self, fileName):
        """
        Open an asset using ACCESS_STREAMING mode.  This provides access to 
        files that have been bundled with an application as assets -- that is, 
        files placed in to the "assets" directory.
        :param fileName: String: The name of the asset to open.  This name can 
        be hierarchical.This value must never be null.
        :return: InputStream. This value will never be null.
        :raises: IOException
        See also: open(String, int)list(String)
        """
        pass

    def openFd(self, fileName):
        """
        Open an uncompressed asset by mmapping it and returning an 
        AssetFileDescriptor. This provides access to files that have been 
        bundled with an application as assets -- that is, files placed in to 
        the "assets" directory.  The asset must be uncompressed, or an 
        exception will be thrown.
        :param fileName: String: The name of the asset to open.  This name can 
        be hierarchical.This value must never be null.
        :return: AssetFileDescriptor. An open AssetFileDescriptor. This value 
        will never be null.
        :raises: IOException
        """
        pass

    @overload('str')
    def openNonAssetFd(self, fileName):
        """
        Open a non-asset as an asset by mmapping it and returning an 
        AssetFileDescriptor. This provides direct access to all of the files 
        included in an application package (not only its assets).  
        Applications should not normally use this.  The asset must not be 
        compressed, or an exception will be thrown.
        :param fileName: String: Name of the asset to retrieve. This value 
        must never be null.
        :return: AssetFileDescriptor. This value will never be null.
        :raises: IOException
        """
        pass

    @openNonAssetFd.adddef('int', 'String')
    def openNonAssetFd(self, cookie, fileName):
        """
        Open a non-asset as an asset by mmapping it and returning an 
        AssetFileDescriptor. This provides direct access to all of the files 
        included in an application package (not only its assets).  
        Applications should not normally use this.  The asset must not be 
        compressed, or an exception will be thrown.
        :param cookie: int: Identifier of the package to be opened.
        :param fileName: String: Name of the asset to retrieve. This value 
        must never be null.
        :return: AssetFileDescriptor. This value will never be null.
        :raises: IOException
        """
        pass

    @overload('int', 'str')
    def openXmlResourceParser(self, cookie, fileName):
        """
        Retrieve a parser for a compiled XML file.
        :param cookie: int: Identifier of the package to be opened.
        :param fileName: String: The name of the file to retrieve. This value 
        must never be null.
        :return: XmlResourceParser. This value will never be null.
        :raises: IOException
        """
        pass

    @openXmlResourceParser.adddef('str')
    def openXmlResourceParser(self, fileName):
        """
        Retrieve a parser for a compiled XML file.
        :param fileName: String: The name of the file to retrieve. This value 
        must never be null.
        :return: XmlResourceParser. This value will never be null.
        :raises: IOException
        """
        pass

    def finalize(self):
        """
        Called by the garbage collector on an object when garbage collection 
        determines that there are no more references to the object. A subclass 
        overrides the finalize method to dispose of system resources or to 
        perform other cleanup.  The general contract of finalize is that it is 
        invoked if and when the Java&trade; virtual machine has determined 
        that there is no longer any means by which this object can be accessed 
        by any thread that has not yet died, except as a result of an action 
        taken by the finalization of some other object or class which is ready 
        to be finalized. The finalize method may take any action, including 
        making this object available again to other threads; the usual purpose 
        of finalize, however, is to perform cleanup actions before the object 
        is irrevocably discarded. For example, the finalize method for an 
        object that represents an input/output connection might perform 
        explicit I/O transactions to break the connection before the object is 
        permanently discarded.  The finalize method of class Object performs 
        no special action; it simply returns normally. Subclasses of Object 
        may override this definition.  The Java programming language does not 
        guarantee which thread will invoke the finalize method for any given 
        object. It is guaranteed, however, that the thread that invokes 
        finalize will not be holding any user-visible synchronization locks 
        when finalize is invoked. If an uncaught exception is thrown by the 
        finalize method, the exception is ignored and finalization of that 
        object terminates.  After the finalize method has been invoked for an 
        object, no further action is taken until the Java virtual machine has 
        again determined that there is no longer any means by which this 
        object can be accessed by any thread that has not yet died, including 
        possible actions by other objects or classes which are ready to be 
        finalized, at which point the object may be discarded.  The finalize 
        method is never invoked more than once by a Java virtual machine for 
        any given object.  Any exception thrown by the finalize method causes 
        the finalization of this object to be halted, but is otherwise ignored.
        :raises: Throwable
        """
        pass
