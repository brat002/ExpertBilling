# A very simple setup script to create a single executable
#
# hello.py is a very simple "Hello, world" type script which also displays the
# environment in which the script runs
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

from cx_Freeze import setup, Executable

executables = [
        Executable("core.py"),
        Executable("nf.py"),
        Executable("rad.py")
]
                
buildOptions = dict(
        compressed = True,
        optimize = True,
        includes = ["encodings.idna","encodings.ascii","encodings.utf_8", "psycopg2.tz"],
    )
                        
setup(
        name = "ebs",
        version = "0.2",
        description = "EBS Core Application",
        options = dict(build_exe = buildOptions),
        executables = executables)

#python setup_core.py build_exe --create-shared-zip --append-script-to-exe --copy-dependent-files