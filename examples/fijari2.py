from PyQt5 import QtGui, QtCore, QtWidgets

import numpy
z = numpy.zeros([256, 384])

def main():
    print("Main method starting")

    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed( True )
    print("Created QT app")

    def run_on_start():
        print( 'single shot in event loop' )

# WORKS
#        import imglyb
#        img = imglyb.to_imglib(z)
#        imglyb.util.BdvFunctions.show(img, "Hello world")

# WORKS
#        import jnius
#        JFrame = jnius.autoclass('javax.swing.JFrame')
#        f = JFrame("Hello")
#        f.setSize(300, 300)
#        f.setVisible(True)
#        print( 'JFrame shown' )

# WORKS WITH JAVA 8, NOT JAVA 11 YET
#        import scyjava_config
#        scyjava_config.add_repositories(scijava=scyjava_config.maven_scijava_repository())
#        scyjava_config.add_endpoints('net.imagej:imagej:2.0.0-rc-71')
#        import scyjava
#        from jnius import autoclass
#        print('1')
#        ImageJ = autoclass('net.imagej.ImageJ')
#        print('2')
#        ij = ImageJ()
#        print('3')
#        ij.ui().showUI()
#        print('4')

# WORKS
        import scyjava_config
#        scyjava_config.add_options('-Djava.awt.headless=true')
#        scyjava_config.add_options('-Xmx' + max_mem_mb + 'm')
        scyjava_config.add_repositories(scijava=scyjava_config.maven_scijava_repository())
        scyjava_config.add_endpoints('net.imagej:imagej', 'org.scijava:scijava-common:2.81.0', 'net.imagej:imagej-common:0.29.2', 'net.imglib2:imglib2-imglyb:0.3.1')
        import scyjava
        from jnius import autoclass
        EventQueue = autoclass('java.awt.EventQueue')
        isEDT = EventQueue.isDispatchThread()
        print(f'isEDT? {isEDT}')

        def start_imagej():
            print('Starting ImageJ on its own thread')
            import imagej
            ij = imagej.init(headless=False, new_instance=True)
            print(ij.getVersion())
            ij.launch()
            if 'viewer' in globals():
                global viewer
                if viewer:
                    viewer.ij = ij
    #        ij.ui().showUI()
            print("Launched ImageJ")

        import threading
        t = threading.Thread( target=start_imagej )
        t.start()

        print('Returning from run_on_start()')
#        app.quit()

    import napari
    print('--> Starting napari')
    global viewer
    viewer = napari.Viewer()
    print('--> napari started')

    print('--> Starting ImageJ via QT')
    QtCore.QTimer.singleShot( 0, run_on_start )
    print('--> Back on the main thread after ImageJ start')

    print ( "Entering qt event loop" )
    app.exec_()

    print('--> I did all the things!')

    import time
    time.sleep(1000000)


if __name__ == "__main__":
    main()
