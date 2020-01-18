

代码导入多进程模块,windows生成单文件模式，运行时卡死



# Recipe Multiprocessing

[Edit](https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing/_edit)[New Page](https://github.com/pyinstaller/pyinstaller/wiki/_new)

Hartmut Goebel edited this page on 26 Nov 2017 · [7 revisions](https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing/_history)

## Required Changes to your code

When using the `multiprocessing` module, you **must** call

```
multiprocessing.freeze_support()
```

straight after the `if __name__ == '__main__':` line of the main module.

Please read the [Python library manual about multiprocessing.freeze_support](http://docs.python.org/library/multiprocessing.html#multiprocessing.freeze_support) for more information.

## Additional code for PyInstaller < 3.3 and Windows

**As of PyInstaller 3.3. adding this code is not longer required, it is already added by a run-time hook.**

On Windows, Multiprocessing code fails when using a --onefile executable. This problem is specific to Windows, which does not support `spawn()`. It does not occur when using the default (--onedir) mode neither does it occur on other (Posix) platforms like all flavors of Unix and Mac OS X.

For using python module `_multiprocess_` on Windows, you need to extend your multiprocessing code as shown below. See [this thread](http://groups.google.com/group/pyinstaller/browse_thread/thread/92971b773203af57/0a2ac0a57ba7f3b0?hl=en#0a2ac0a57ba7f3b0) about the background and ticket <https://github.com/pyinstaller/pyinstaller/issues/182> for more information.

This recipe requires PyInstaller 3.0 < 3.3.

```
import os
import sys

# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen
```

Example for testing multiprocessing:

```
import multiprocessing

class SendeventProcess(multiprocessing.Process):
    def __init__(self, resultQueue):
        self.resultQueue = resultQueue
        multiprocessing.Process.__init__(self)
        self.start()

    def run(self):
        print 'SendeventProcess'
        self.resultQueue.put((1, 2))
        print 'SendeventProcess'


if __name__ == '__main__':
    # On Windows calling this function is necessary.
    # On Linux/OSX it does nothing.
    multiprocessing.freeze_support()
    print 'main'
    resultQueue = multiprocessing.Queue()
    SendeventProcess(resultQueue)
    print 'main'
```

Console output of this code snippet should be similar to

```
main
main
SendeventProcess
SendeventProcess
```

