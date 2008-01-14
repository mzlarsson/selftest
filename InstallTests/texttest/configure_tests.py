#!/usr/bin/env python

# Transform the TextTest self-tests according to the local environment, depending on what
# operating system is being run and what software is installed locally.

# Usage : configure_tests.py [ -d <test_dir> ] [ -c <source_dir> ] 

# The test directory to change is found in the same way as in TextTest: i.e. it looks
# at the -d option on the command line, the environment variable TEXTTEST_HOME and then the current
# working directory.

# If you've put your TextTest source somewhere else you should tell it that too so
# you can change the defaults. Use the -c option. Otherwise it will assume the tarball
# is intact

try:
    import configintercept # The classic test-handle...
except ImportError:
    pass

import sys, os, shutil
from getopt import getopt
from tempfile import mktemp

def findPathsMatching(dir, stem):
    paths = []
    for file in os.listdir(dir):
        fullPath = os.path.join(dir, file)
        if file == stem or file.startswith(stem + "."):
            paths.append(fullPath)
        elif os.path.isdir(fullPath) and file != "InstallTests":
            # Don't touch the InstallTests, they exist to test this script!
            paths += findPathsMatching(fullPath, stem)
    return paths

def commentLine(file, text):
    return transformFile(file, insertComment, text)

def uncommentLine(file, text):
    return transformFile(file, removeComment, text)

def transformFile(file, function, *args):
    newFileName = mktemp("tmp_config")
    newFile = open(newFileName, "w")
    changed = False
    for line in open(file).xreadlines():
        newLine = function(line, *args)
        if newLine is None:
            print line + "-> removed from " + file
            changed = True
            continue
        if newLine != line:
            changed = True
            print newLine + "-> inserted into " + file
        newFile.write(newLine)
    newFile.close()
    if changed:
        shutil.move(newFileName, file)
    else:
        os.remove(newFileName)

def insertIntoConfig(line, extraLine):
    if line.startswith("binary:"):
        return line + "\n" + extraLine + "\n"
    else:
        return line
    
def insertComment(line, text):
    if line.strip() == text:
        return "# " + line
    else:
        return line

def removeComment(line, text):
    if line.startswith("#") and line.strip().endswith(text):
        return line.replace("#", "").lstrip()
    else:
        return line

# DOS shells have $$ as a special character, need to double it up
def replaceDollarForWindows(line):
    if line.rstrip().endswith("$") or line.find("$ ") != -1:
        return line.replace("$", "$$")
    else:
        return line

# Default viewing tools are different for windows
def replaceToolsForWindows(line):
    if line.find("'tail") != -1 or line.find("\"tail") != -1:
        return line.replace("tail -f", "baretail").replace("'tail'", "'baretail'")
    return line.replace("emacs", "notepad")

def replaceCmdToolsForWindows(line):
    return line.replace("emacs window", "notepad window")

def replaceDisplayForWindows(line):
    pos = line.find("DISPLAY variable set to")
    if pos != -1:
        return line.replace(line[pos:], "windows hidden\n")
    if line.find("Xvfb process") == -1:
        return line
    
# Windows needs ; as path separator instead of :
def replacePathForWindows(line):
    if line.find("PATH:") != -1:
        return line.replace(":", ";").replace("PATH;", "PATH:")
    else:
        return line
 
def isInstalled(program):
    for dir in os.getenv("PATH").split(os.pathsep):
        fullPath = os.path.join(dir, program)
        if os.path.isfile(fullPath):
            return True
    return False

def getPreRequisites():
    common = [ "tkdiff", "java" ]
    if os.name == "posix":
        return common + [ "emacs", "tail", "Xvfb" ]
    else:
        allStems = common + [ "wordpad", "baretail" ]
        return [ name + ".exe" for name in allStems ] 

def checkPreRequisites():
    for program in getPreRequisites():
        if not isInstalled(program):
            raise EnvironmentError, "pre-requisite program '" + program + "' cannot be found on your PATH."

def enableQueueSystem(name, configFile):
    print name, "is installed - changing self-tests to run in parallel using it"
    transformFile(configFile, insertIntoConfig, "config_module:queuesystem\nqueue_system_module:" + name)
            
def configureTests(testDir, sourceDir):
    checkPreRequisites()
    testSuiteFiles = findPathsMatching(testDir, "testsuite")
    configFile = os.path.join(testDir, "config.texttest")
    instConfigFile = os.path.join(testDir, "config.ttinst")
    if os.name == "posix":
        if isInstalled("qsub"):
            enableQueueSystem("SGE", configFile)
        elif isInstalled("bsub"):
            enableQueueSystem("LSF", configFile)
    else:
        print "Disabling UNIX-specific test elements..."
        commentLine(configFile, "view_program:emacs")
        commentLine(configFile, "extra_version:lsf")
        commentLine(configFile, "extra_version:sge")
        for testSuiteFile in testSuiteFiles:
            commentLine(testSuiteFile, "UnixOnly")
            uncommentLine(testSuiteFile, "WindowsOnly")
        print "Replacing PATH settings in environment files ':' -> ';'"
        for envFile in findPathsMatching(testDir, "environment"):
            transformFile(envFile, replacePathForWindows)
        print "Replacing for MS-DOS syntax in options and config files '$' -> '$$'"
        configFiles = findPathsMatching(testDir, "config")
        filesWithDollars = findPathsMatching(testDir, "options") + configFiles
        for fileWithDollars in filesWithDollars:
            transformFile(fileWithDollars, replaceDollarForWindows)
        filesWithTools = findPathsMatching(testDir, "gui_log") + \
                         findPathsMatching(testDir, "dynamic_gui_log") + configFiles
        for fileWithTools in filesWithTools:
            transformFile(fileWithTools, replaceToolsForWindows)

        for outputFile in findPathsMatching(testDir, "output"):
            transformFile(outputFile, replaceCmdToolsForWindows)
        filesWithDisplay = findPathsMatching(testDir, "outputrep") + findPathsMatching(testDir, "outputdyn")
        for outputFile in filesWithDisplay:
            transformFile(outputFile, replaceDisplayForWindows)
        # Files come from UNIX, which don't get displayed properly by notepad (the default)
        transformFile(configFile, insertIntoConfig, "view_program:wordpad")
        transformFile(instConfigFile, insertIntoConfig, "view_program:wordpad")
    
    transformFile(configFile, insertIntoConfig, "checkout_location:" + sourceDir)
    transformFile(instConfigFile, insertIntoConfig, "checkout_location:" + testDir)
    try:
        import gtk
    except:
        print "PyGTK is not installed locally, so you will not be able to run the TextTest GUI."
        print "See the README for downloading instructions."
        for testSuiteFile in testSuiteFiles:
            commentLine(testSuiteFile, "GUI")

def getCheckout(optDict):
    if optDict.has_key("-c"):
        return optDict.get("-c")
    localDir = os.path.dirname(os.path.abspath(sys.argv[0]))
    installRoot = os.path.dirname(os.path.dirname(localDir))
    sourceDir = os.path.join(installRoot, "source")
    if os.path.isdir(sourceDir):
        return sourceDir
    else:
        print "No source directory found at", sourceDir, ": please specify it with the -c option."

        
def getTestDir(root):
    ttSubDir = os.path.join(root, "texttest")
    if os.path.isdir(ttSubDir):
        return ttSubDir
    else:
        return root

def getCommandLine():
    options, leftovers = getopt(sys.argv[1:], "d:c:")
    optDict = dict(options)
    return optDict.get("-d", os.getenv("TEXTTEST_HOME", os.getcwd())), getCheckout(optDict)
    
if __name__ == "__main__":
    testRoot, sourceDir = getCommandLine()
    if sourceDir:
        testDir = getTestDir(testRoot)
        try:
            configureTests(testDir, sourceDir)
        except EnvironmentError, e:
            print "ERROR: Could not run self-tests as", str(e)
            sys.exit(1)
