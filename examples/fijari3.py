from PyQt5 import QtCore, QtWidgets

def main():
    print("Main method starting")

    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed( True )
    print("Created QT app")

    def start_imagej():
        print( 'single shot in event loop' )

        import imagej
        ij = imagej.init(headless=False)

        from jnius import PythonJavaClass, java_method, autoclass
        class JavaRunnable(PythonJavaClass):
            __javainterfaces__ = ['java/lang/Runnable']

            def __init__(self, f):
                super(JavaRunnable, self).__init__()
                self._f = f

            @java_method('()V')
            def run(self):
                self._f()

        
        class HackedUIService(object):
            def __init__(self, ij):
                super(HackedUIService, self).__init__()
                self._ij = ij
            def __getattr__(self, name):
                value = getattr(ij.ui(), name)
                if str(type(value)) in ['jnius.JavaMethod', 'jnius.JavaMultipleMethod']:
                    return lambda: ij.thread().queue(JavaRunnable(lambda: value(kwargs)))
                return value
        p_ui = HackedUIService(ij)
        ij.ui = lambda: p_ui

        print(ij.getVersion())
        ij.launch()
        print("Launched ImageJ")

    print('--> Starting ImageJ via QT')
    QtCore.QTimer.singleShot(0, start_imagej)
    print('--> Back on the main thread after ImageJ start')

    print ( "Entering qt event loop" )
    app.exec_()

    print('--> I did all the things!')


if __name__ == "__main__":
    main()
