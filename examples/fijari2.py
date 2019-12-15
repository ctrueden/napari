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
        import imagej
#        ij = imagej.init('net.imagej:imagej', headless=False)
        ij = imagej.init('sc.fiji:fiji+net.imagej:imagej-legacy:0.37.1-SNAPSHOT', headless=False)
        print(ij.getVersion())
        ij.launch()
        if 'viewer' in globals():
            global viewer
            if viewer:
                viewer.ij = ij
#        ij.ui().showUI()
        print("Launched ImageJ")

        # TODO: Determine whether this is really necessary.
        # In Philipp's experience, Python quits if you don't keep it alive --
        # even when Java still has things including GUI going on.
        import jnius, time
        Window = jnius.autoclass('java.awt.Window')
        System = jnius.autoclass('java.lang.System')
        def sleeper():
            # NB: Quit when all Java AWT windows are gone.
            while any(True for w in Window.getWindows() if w.isVisible()):
                time.sleep( 0.1 )
            System.exit(0)

        import threading
        t = threading.Thread( target=sleeper )
        t.start()

        print('Returning from run_on_start()')

    import napari
    print('--> Starting napari')
    global viewer
    viewer = napari.Viewer()
    print('--> napari started')

    print('--> Starting ImageJ via QT')

    QtCore.QTimer.singleShot( 0, run_on_start )

    print ( "Entering qt event loop" )
    app.exec_()

    print('--> I did all the things!')

    import time
    time.sleep(1000000)


if __name__ == "__main__":
    main()
