/*
 * napari macOS launcher
 *
 * This small binary exists so that the macOS menu bar displays "napari"
 * rather than the Python interpreter name. macOS derives the application
 * name displayed in the menu bar exclusively from the process image
 * (Mach-O binary) name; no runtime API can override this.
 *
 * It is invoked via os.execv() from napari/__main__.py:main() before any
 * Qt or napari code is imported. argv layout (set by the Python caller):
 *
 *   argv[0]  path to this binary (ignored beyond argc check)
 *   argv[1]  absolute path to libpython3.X.dylib
 *   argv[2]  absolute path to the real python executable
 *   argv[3]  "-m"
 *   argv[4]  "napari"
 *   argv[5+] original command-line arguments from the user
 *
 * Py_BytesMain is called with (argc-2, argv+2), so Python sees:
 *   argv[0]  real python path  -> sets sys.executable correctly
 *   argv[1]  "-m"
 *   argv[2]  "napari"
 *   argv[3+] user args
 *
 * Build (universal binary):
 *   clang -arch arm64  launcher.c -o napari_arm64
 *   clang -arch x86_64 launcher.c -o napari_x86_64
 *   lipo -create napari_arm64 napari_x86_64 -output napari
 *   rm napari_arm64 napari_x86_64
 *
 * No Python headers or libraries are needed at compile time.
 */

#include <dlfcn.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr,
            "napari launcher: expected at least 5 arguments "
            "(self, libpython, python_exe, -m, napari)\n");
        return 1;
    }

    const char  *libpython_path = argv[1];
    int          python_argc    = argc - 2;
    char       **python_argv    = argv + 2;
    /* python_argv[0] = real python exe  -> sets sys.executable correctly */
    /* python_argv[1:] = ["-m", "napari", ...user args...]               */

    void *lib = dlopen(libpython_path, RTLD_LAZY | RTLD_GLOBAL);
    if (!lib) {
        fprintf(stderr,
            "napari launcher: failed to load %s: %s\n",
            libpython_path, dlerror());
        return 1;
    }

    typedef int (*py_bytes_main_t)(int, char **);
    py_bytes_main_t py_main =
        (py_bytes_main_t)dlsym(lib, "Py_BytesMain");
    if (!py_main) {
        fprintf(stderr,
            "napari launcher: Py_BytesMain not found in %s\n",
            libpython_path);
        return 1;
    }

    return py_main(python_argc, python_argv);
}
