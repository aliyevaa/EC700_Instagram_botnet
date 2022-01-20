import subprocess, os, random
import time 

class adb:
    def __init__(self, device=None):
        self.device = device

        if(device):
            self.command = 'adb -s ' + device + ' '
        else:
            self.command = 'adb '

    def set_device(self, device):
        self.command = 'adb -s ' + device

    def shell(self, cmd):
        return self._runCommand(self.command + 'shell \'%s\'' % cmd)

    def su_shell(self, cmd):
        return self.shell("su -c '\"" + cmd + "\"'")

    def input(self, cmd):
        return self.shell('input ' + cmd)

    def tap(self, x, y):
        return self.input('tap %d %d' % (x,y))

    def input_text(self, text): 
        self.input('text ' + text)

    def input_keyevent(self, keycode):
        return self.input('keyevent %s' % str(keycode))

    def clear_text(self):
        self.input_keyevent('KEYCODE_MOVE_END')
        for i in range(0,250):
            self.input_keyevent('--longpress KEYCODE_DEL')

    def push(self, src, dst):
        return self._runCommand(self.command + 'push ' + src + ' ' + dst)

    def install(self, package):
        print(self.command + 'install ' + package)
        print("package = ", package)
        return self._runCommand(self.command + 'install ' + package)

    def uninstall(self, package):
        return self._runCommand(self.command + 'uninstall ' + package)

    def open(self, package):
        #self.shell('pm grant '+ package + " android.permission.READ_EXTERNAL_STORAGE")
        #self.shell('pm grant '+ package + " android.permission.WRITE_EXTERNAL_STORAGE")
        #self.shell('rm /sdcard/rrtraces/*')
        #self.shell('cp /sdcard/config /sdcard/rrtraces/config')
        return self.shell('monkey -p ' + package + ' -c android.intent.category.LAUNCHER 1')
    
    def close(self, package):
        return self.shell('am force-stop ' + package)

    def screenshot(self, dst):
        self.shell('screencap -p /sdcard/temp_screen.png')
        self.pull('/sdcard/temp_screen.png', dst)

    def dump_layout(self):
        return self._runCommand(self.command + 'exec-out uiautomator dump /dev/tty')[0].decode("utf-8")[:-33]

    def get_focused_app(self):
        return self.shell('dumpsys window windows | grep -E \'mCurrentFocus\' | cut -d " " -f 5 | cut -d "/" -f 1')[0].decode('utf-8').strip()

    def check_package(self, package):
        out = self.shell('pm list packages')
        if package in str(out[0]):
            return True
        return False

    def check_if_off(self):
        out = self.shell('dumpsys window policy')
        if "mAwake=false" in str(out[0]):
            return True
        return False

    def unlock(self):
        self.shell("input keyevent 26")	
        self.shell("input touchscreen swipe 930 980 930 280")
        return
    
    def lock(self):
        self.shell("input keyevent 26")
        return

    def _runCommand(self, cmd):
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE,
               stderr=subprocess.STDOUT, shell=True)
        return out.communicate()
