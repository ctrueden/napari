#!/usr/bin/env python

#
# scifio.py - Open images as numpy arrays using SCIFIO and Bio-Formats.
#

# -- Settings --

max_mem_mb = '6144'
scifio_lifesci = False
bio_formats = True


# -- Bill of Materials --

imagej_version = '2.0.0-rc-71'
scifio_version = '0.38.2'
scifio_bf_compat_version = '4.0.0'
scifio_lifesci_version = '0.9.0'
bio_formats_version = '6.3.0'


# -- Functions --

def dtype_from_meta(image_meta):
    FormatTools = autoclass('io.scif.util.FormatTools')
    endianness = '<' if image_meta.isLittleEndian() else '>'
    pixel_types = {
        FormatTools.INT8: 'i1',
        FormatTools.UINT8: 'u1',
        FormatTools.INT16: 'i2',
        FormatTools.UINT16: 'u2',
        FormatTools.INT32: 'i4',
        FormatTools.UINT32: 'u4',
        FormatTools.FLOAT: 'f4',
        FormatTools.DOUBLE: 'f8'
    }
    pixel_type = pixel_types[image_meta.getPixelType()]
    return endianness + pixel_type

def read_images(scifio, image_path):
    import numpy
    from jnius import autoclass, cast

    # Initialize the SCIFIO reader.
    LocationService = autoclass('org.scijava.io.location.LocationService')
    location_service = cast(LocationService, scifio.get(LocationService))
    image_location = location_service.resolve(image_path)
    SCIFIOConfig = autoclass('io.scif.config.SCIFIOConfig')
    scifio_config = SCIFIOConfig()
    scifio_config.groupableSetGroupFiles(True)
    print('scifio_config = {}'.format(scifio_config))
    reader = scifio.initializer().initializeReader(image_location, scifio_config)
    meta = reader.getMetadata()

    images = []
    # Iterate over each nD image in the dataset.
    for i in range(0, reader.getImageCount()):
        # Query image type and dimensions.
        image_meta = meta.get(i)
        dtype = dtype_from_meta(image_meta)
        planar_axis_lengths = [image_meta.getAxisLength(p) for p in reversed(range(image_meta.getPlanarAxisCount()))]
        all_axis_lengths = list(reversed(image_meta.getAxesLengths()))

        # Iterate over each mD (m <= n; often m=2 or m=3) plane in the image.
        planes = []
        for p in range(0, reader.getPlaneCount(i)):
            b = reader.openPlane(i, p).getBytes()
            plane = numpy.frombuffer(bytes(b), dtype=dtype).reshape(planar_axis_lengths)
            planes.append(plane)

        image = numpy.concatenate(planes).reshape(all_axis_lengths)
        images.append(image)

    return images

def jstacktrace(exc):
    if not hasattr(exc, 'classname') or exc.classname is None:
        return str(exc)
    return '' if not exc.stacktrace else '\n\tat '.join(exc.stacktrace)


# -- Main --

# Initialize SCIFIO with desired plugins.
import scyjava_config
scyjava_config.add_options('-Djava.awt.headless=true')
scyjava_config.add_options('-Xmx' + max_mem_mb + 'm')
endpoint = 'io.scif:scifio:{}'.format(scifio_version)
# Failed attempt to silence log4j and SLF4J warnings:
endpoint += '+org.slf4j:log4j-over-slf4j:1.7.28'
endpoint += '+org.slf4j:slf4j-simple:1.7.28'
if scifio_lifesci:
    endpoint += '+io.scif:scifio-lifesci:{}'.format(scifio_lifesci_version)
if bio_formats:
    endpoint += '+io.scif:scifio-bf-compat:{}'.format(scifio_bf_compat_version)
    endpoint += '+ome:formats-api:{}'.format(bio_formats_version)
    endpoint += '+ome:formats-bsd:{}'.format(bio_formats_version)
    endpoint += '+ome:formats-gpl:{}'.format(bio_formats_version)
scyjava_config.add_repositories({'scijava.public': scyjava_config.maven_scijava_repository()})
scyjava_config.add_endpoints(endpoint)
import scyjava
from jnius import autoclass
SCIFIO = autoclass('io.scif.SCIFIO')
scifio = SCIFIO()

# Dump the class path, for debugging.
#import re
#from jnius import autoclass
#System = autoclass('java.lang.System')
#java_class_path = System.getProperty('java.class.path')
#print('Java class path:')
#for element in java_class_path.split(':'):
#    print('\t' + re.sub('.*/', '', element))

# Read an image.
import sys
for i in range(1, len(sys.argv)):
    path = sys.argv[i]
    try:
        print('[{}]'.format(path))
        images = read_images(scifio, path)
        print('Image count = {}'.format(len(images)))
        print('First image shape = {}'.format(images[0].shape))
        print()
    except Exception as exc:
        print(jstacktrace(exc))

# Clean up.
#scifio.getContext().dispose()
