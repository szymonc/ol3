#!/usr/bin/env python

from cStringIO import StringIO
import gzip
import json
import os
import os.path
import re
import shutil
import sys

from pake import Target, ifind, main, output, rule, target, variables, virtual


if sys.platform == 'win32':
    ProgramFiles = os.environ.get('ProgramFiles', 'C:\\Program Files')
    ProgramFiles_X86 = os.environ.get('ProgramFiles(X86)', 'C:\\Program Files')
    Python27 = os.environ.get('SystemDrive', 'C:') + '\\Python27'
    variables.GIT = os.path.join(ProgramFiles_X86, 'Git', 'bin', 'git.exe')
    variables.GJSLINT = os.path.join(Python27, 'Scripts', 'gjslint.exe')
    variables.JAVA = os.path.join(
        ProgramFiles, 'Java', 'jre7', 'bin', 'java.exe')
    variables.JSDOC = 'jsdoc'  # FIXME
    variables.NODE = 'node'
    variables.PYTHON = os.path.join(Python27, 'python.exe')
    variables.PHANTOMJS = 'phantomjs.exe'
else:
    variables.GIT = 'git'
    variables.GJSLINT = 'gjslint'
    variables.JAVA = 'java'
    variables.JAR = 'jar'
    variables.JSDOC = 'jsdoc'
    variables.NODE = 'node'
    variables.PYTHON = 'python'
    variables.PHANTOMJS = 'phantomjs'

TEMPLATE_GLSL_COMPILER_JS = 'build/glsl-unit/bin/template_glsl_compiler.js'

variables.BRANCH = output(
    '%(GIT)s', 'rev-parse', '--abbrev-ref', 'HEAD').strip()

EXPORTS = [path
           for path in ifind('src')
           if path.endswith('.exports')
           if path != 'src/objectliterals.exports']

EXTERNAL_SRC = [
    'build/src/external/externs/types.js',
    'build/src/external/src/exports.js',
    'build/src/external/src/types.js']

EXAMPLES = [path
            for path in ifind('examples')
            if path.endswith('.html')
            if path != 'examples/index.html']

EXAMPLES_SRC = [path
                for path in ifind('examples')
                if path.endswith('.js')
                if not path.endswith('.combined.js')
                if not path.startswith('examples/bootstrap')
                if not path.startswith('examples/font-awesome')
                if path != 'examples/Jugl.js'
                if path != 'examples/jquery.min.js'
                if path != 'examples/example-list.js']

EXAMPLES_JSON = ['build/' + example.replace('.html', '.json')
                 for example in EXAMPLES]

EXAMPLES_COMBINED = ['build/' + example.replace('.html', '.combined.js')
                     for example in EXAMPLES]

INTERNAL_SRC = [
    'build/src/internal/src/requireall.js',
    'build/src/internal/src/types.js']

GLSL_SRC = [path
            for path in ifind('src')
            if path.endswith('.glsl')]

SHADER_SRC = [path.replace('.glsl', 'shader.js')
              for path in GLSL_SRC]

SPEC = [path
        for path in ifind('test/spec')
        if path.endswith('.js')]

SRC = [path
       for path in ifind('src/ol')
       if path.endswith('.js')
       if path not in SHADER_SRC]

PLOVR_JAR = 'build/plovr-eba786b34df9.jar'
PLOVR_JAR_MD5 = '20eac8ccc4578676511cf7ccbfc65100'

PROJ4JS = 'build/proj4js/lib/proj4js-combined.js'
PROJ4JS_ZIP = 'build/proj4js-1.1.0.zip'
PROJ4JS_ZIP_MD5 = '17caad64cf6ebc6e6fe62f292b134897'


def report_sizes(t):
    t.info('uncompressed: %d bytes', os.stat(t.name).st_size)
    stringio = StringIO()
    gzipfile = gzip.GzipFile(t.name, 'w', 9, stringio)
    with open(t.name) as f:
        shutil.copyfileobj(f, gzipfile)
    gzipfile.close()
    t.info('  compressed: %d bytes', len(stringio.getvalue()))


virtual('default', 'build')


virtual('integration-test', 'lint', 'build', 'build-all',
        'test', 'build-examples', 'check-examples', 'doc')


virtual('build', 'build/ol.css', 'build/ol.js',
        'build/ol-simple.js', 'build/ol-whitespace.js')


virtual('check', 'lint', 'build/ol.css', 'build/ol.js', 'test')


virtual('todo', 'fixme')


@target('build/ol.css', 'build/ol.js')
def build_ol_css(t):
    t.touch()


@target('build/ol.js', PLOVR_JAR, SRC, EXTERNAL_SRC, SHADER_SRC,
        'buildcfg/base.json', 'buildcfg/ol.json')
def build_ol_js(t):
    t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build', 'buildcfg/ol.json')
    report_sizes(t)


@target('build/ol-simple.js', PLOVR_JAR, SRC, INTERNAL_SRC, SHADER_SRC,
        'buildcfg/base.json', 'buildcfg/ol.json', 'buildcfg/ol-simple.json')
def build_ol_simple_js(t):
    t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build', 'buildcfg/ol-simple.json')
    report_sizes(t)


@target('build/ol-whitespace.js', PLOVR_JAR, SRC, INTERNAL_SRC, SHADER_SRC,
        'buildcfg/base.json', 'buildcfg/ol.json',
        'buildcfg/ol-whitespace.json')
def build_ol_whitespace_js(t):
    t.output('%(JAVA)s', '-jar', PLOVR_JAR,
             'build', 'buildcfg/ol-whitespace.json')
    report_sizes(t)


virtual('build-all', 'build/ol-all.js')


@target('build/ol-all.js', PLOVR_JAR, SRC, INTERNAL_SRC, SHADER_SRC,
        'buildcfg/base.json', 'buildcfg/ol-all.json')
def build_ol_all_js(t):
    t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build', 'buildcfg/ol-all.json')


@target('build/src/external/externs/types.js', 'bin/generate-exports.py',
        'src/objectliterals.exports')
def build_src_external_externs_types_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py',
             '--externs', 'src/objectliterals.exports')


@target('build/src/external/src/exports.js', 'bin/generate-exports.py',
        'src/objectliterals.exports', EXPORTS)
def build_src_external_src_exports_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py',
             '--exports', 'src/objectliterals.exports', EXPORTS)


@target('build/src/external/src/types.js', 'bin/generate-exports.py',
        'src/objectliterals.exports')
def build_src_external_src_types_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py',
             '--typedef', 'src/objectliterals.exports')


if os.path.exists(TEMPLATE_GLSL_COMPILER_JS):
    for glsl_src in GLSL_SRC:
        def shader_src_helper(glsl_src):
            @target(glsl_src.replace('.glsl', 'shader.js'), glsl_src,
                    'src/ol/webgl/shader.mustache')
            def shader_src(t):
                t.run('%(NODE)s', TEMPLATE_GLSL_COMPILER_JS,
                      '--input', glsl_src,
                      '--template', 'src/ol/webgl/shader.mustache',
                      '--output', t.name)
        shader_src_helper(glsl_src)


def _build_require_list(dependencies, output_file_name):
    requires = set()
    for dependency in dependencies:
        for line in open(dependency):
            match = re.match(r'goog\.provide\(\'(.*)\'\);', line)
            if match:
                requires.add(match.group(1))
    with open(output_file_name, 'w') as f:
        for require in sorted(requires):
            f.write('goog.require(\'%s\');\n' % (require,))


@target('build/src/internal/src/requireall.js', SRC, SHADER_SRC)
def build_src_internal_src_requireall_js(t):
    _build_require_list(t.dependencies, t.name)


@target('build/test/requireall.js', SPEC)
def build_test_requireall_js(t):
    _build_require_list(t.dependencies, t.name)


@target('build/src/internal/src/types.js', 'bin/generate-exports.py',
        'src/objectliterals.exports')
def build_src_internal_types_js(t):
    t.output('%(PYTHON)s', 'bin/generate-exports.py',
             '--typedef', 'src/objectliterals.exports')


virtual('build-examples', 'examples', EXAMPLES_COMBINED)


virtual('examples', 'examples/example-list.xml', EXAMPLES_JSON)


@target('examples/example-list.xml', 'examples/example-list.js')
def examples_examples_list_xml(t):
    t.touch()  # already generated by bin/exampleparser.py


@target('examples/example-list.js', 'bin/exampleparser.py', EXAMPLES)
def examples_examples_list_js(t):
    t.run('%(PYTHON)s', 'bin/exampleparser.py', 'examples', 'examples')


@rule(r'\Abuild/examples/(?P<id>.*).json\Z')
def examples_star_json(name, match):
    def action(t):
        content = json.dumps({
            'id': match.group('id'),
            'inherits': '../../buildcfg/base.json',
            'inputs': [
                '../examples/%(id)s.js' % match.groupdict(),
                '../build/src/internal/src/types.js',
            ],
            'externs': [
                '//json.js',
                '//jquery-1.7.js',
                '../externs/bingmaps.js',
                '../externs/bootstrap.js',
                '../externs/geojson.js',
                '../externs/proj4js.js',
                '../externs/tilejson.js',
            ],
        })
        with open(t.name, 'w') as f:
            f.write(content)
    dependencies = [__file__, 'buildcfg/base.json']
    return Target(name, action=action, dependencies=dependencies)


@rule(r'\Abuild/examples/(?P<id>.*).combined.js\Z')
def examples_star_combined_js(name, match):
    def action(t):
        t.output('%(JAVA)s', '-jar', PLOVR_JAR, 'build',
                 'build/examples/%(id)s.json' % match.groupdict())
        report_sizes(t)
    dependencies = [PLOVR_JAR, SRC, INTERNAL_SRC, SHADER_SRC,
                    'buildcfg/base.json',
                    'examples/%(id)s.js' % match.groupdict(),
                    'build/examples/%(id)s.json' % match.groupdict()]
    return Target(name, action=action, dependencies=dependencies)


@target('serve', PLOVR_JAR, INTERNAL_SRC, 'build/test/requireall.js',
        'examples')
def serve(t):
    t.run('%(JAVA)s', '-jar', PLOVR_JAR, 'serve', 'buildcfg/ol.json',
          'buildcfg/ol-all.json', EXAMPLES_JSON, 'buildcfg/test.json')


@target('serve-integration-test', PLOVR_JAR, INTERNAL_SRC)
def serve_precommit(t):
    t.run('%(JAVA)s', '-jar', PLOVR_JAR, 'serve',
          'buildcfg/ol-all.json', 'buildcfg/test.json')


virtual('lint', 'build/lint-timestamp', 'build/check-requires-timestamp')


@target('build/lint-timestamp', SRC, INTERNAL_SRC, EXTERNAL_SRC, EXAMPLES_SRC,
        SPEC, precious=True)
def build_lint_src_timestamp(t):
    limited_doc_files = [
        path
        for path in ifind('externs', 'build/src/external/externs')
        if path.endswith('.js')]
    t.run('%(GJSLINT)s', '--strict', '--limited_doc_files=%s' %
          (','.join(limited_doc_files),), t.newer(t.dependencies))
    t.touch()


def _strip_comments(lines):
    # FIXME this is a horribe hack, we should use a proper JavaScript parser
    # here
    in_multiline_comment = False
    lineno = 0
    for line in lines:
        lineno += 1
        if in_multiline_comment:
            index = line.find('*/')
            if index != -1:
                in_multiline_comment = False
                line = line[index + 2:]
        if not in_multiline_comment:
            line = re.sub(r'//[^\n]*', '', line)
            line = re.sub(r'/\*.*?\*/', '', line)
            index = line.find('/*')
            if index != -1:
                yield lineno, line[:index]
                in_multiline_comment = True
            else:
                yield lineno, line


@target('build/check-requires-timestamp', SRC, INTERNAL_SRC, EXTERNAL_SRC,
        EXAMPLES_SRC, SHADER_SRC, SPEC)
def build_check_requires_timestamp(t):
    unused_count = 0
    all_provides = set()
    for filename in sorted(t.dependencies):
        if filename == 'build/src/internal/src/requireall.js':
            continue
        require_linenos = {}
        uses = set()
        lines = open(filename).readlines()
        for lineno, line in _strip_comments(lines):
            m = re.match(r'goog.provide\(\'(.*)\'\);', line)
            if m:
                all_provides.add(m.group(1))
                continue
            m = re.match(r'goog.require\(\'(.*)\'\);', line)
            if m:
                require_linenos[m.group(1)] = lineno
                continue
        ignore_linenos = require_linenos.values()
        for lineno, line in enumerate(lines):
            if lineno in ignore_linenos:
                continue
            for require in require_linenos.iterkeys():
                if require in line:
                    uses.add(require)
        for require in sorted(set(require_linenos.keys()) - uses):
            t.info('%s:%d: unused goog.require: %r' % (
                filename, require_linenos[require], require))
            unused_count += 1
    all_provides.discard('ol')
    all_provides.discard('ol.Map')
    all_provides.discard('ol.MapProperty')
    provide_res = [(provide, re.compile(r'\b%s\b' % (re.escape(
        provide)),)) for provide in sorted(all_provides, reverse=True)]
    missing_count = 0
    for filename in sorted(t.dependencies):
        if filename in INTERNAL_SRC or filename in EXTERNAL_SRC:
            continue
        provides = set()
        requires = set()
        uses = set()
        for lineno, line in _strip_comments(open(filename)):
            m = re.match(r'goog.provide\(\'(.*)\'\);', line)
            if m:
                provides.add(m.group(1))
                continue
            m = re.match(r'goog.require\(\'(.*)\'\);', line)
            if m:
                requires.add(m.group(1))
                continue
            for provide, provide_re in provide_res:
                if provide_re.search(line):
                    line = line.replace(provide, '')
                    uses.add(provide)
        if filename == 'src/ol/renderer/layerrenderer.js':
            uses.discard('ol.renderer.Map')
        m = re.match(
            r'src/ol/renderer/(\w+)/\1(\w*)layerrenderer\.js\Z', filename)
        if m:
            uses.discard('ol.renderer.Map')
            uses.discard('ol.renderer.%s.Map' % (m.group(1),))
        missing_requires = uses - requires - provides
        if missing_requires:
            t.info('%s: missing goog.requires: %s', filename, ', '.join(
                sorted(missing_requires)))
            missing_count += len(missing_requires)
    if unused_count or missing_count:
        t.error('%d unused goog.requires, %d missing goog.requires' %
                (unused_count, missing_count))
    t.touch()


virtual('plovr', PLOVR_JAR)


@target(PLOVR_JAR, clean=False)
def plovr_jar(t):
    t.info('downloading %r', t.name)
    t.download('https://plovr.googlecode.com/files/' +
               os.path.basename(PLOVR_JAR), md5=PLOVR_JAR_MD5)
    t.info('downloaded %r', t.name)


@target('gh-pages', 'host-examples', 'doc', phony=True)
def gh_pages(t):
    with t.tempdir() as tempdir:
        t.run('%(GIT)s', 'clone', '--branch', 'gh-pages',
              'git@github.com:openlayers/ol3.git', tempdir)
        with t.chdir(tempdir):
            t.rm_rf('%(BRANCH)s')
        t.cp_r('build/gh-pages/%(BRANCH)s', tempdir + '/%(BRANCH)s')
        with t.chdir(tempdir):
            t.run('%(GIT)s', 'add', '--all', '%(BRANCH)s')
            t.run('%(GIT)s', 'commit', '--message', 'Updated')
            t.run('%(GIT)s', 'push', 'origin', 'gh-pages')


virtual('doc', 'build/jsdoc-%(BRANCH)s-timestamp' % vars(variables))


@target('build/jsdoc-%(BRANCH)s-timestamp' % vars(variables), SRC, SHADER_SRC,
        ifind('doc/template'))
def jsdoc_BRANCH_timestamp(t):
    t.run('%(JSDOC)s', '-t', 'doc/template', '-r',
          'src', '-d', 'build/gh-pages/%(BRANCH)s/apidoc')
    t.touch()


def split_example_file(example, dst_dir):
    lines = open(example).readlines()

    target_lines = []
    target_require_lines = []

    found_requires = False
    found_code = False
    for line in lines:
        m = re.match(r'goog.require\(\'(.*)\'\);', line)
        if m:
            found_requires = True
            target_require_lines.append(line)
        elif found_requires:
            if found_code or line not in ('\n', '\r\n'):
                found_code = True
                target_lines.append(line)

    target = open(
        os.path.join(dst_dir, os.path.basename(example)), 'w')
    target_require = open(
        os.path.join(dst_dir, os.path.basename(example)
          .replace('.js', '-require.js')),
        'w')

    target.writelines(target_lines)
    target.close()

    target_require.writelines(target_require_lines)
    target_require.close()


@target('host-examples', 'build', 'examples', phony=True)
def host_examples(t):
    examples_dir = 'build/gh-pages/%(BRANCH)s/examples'
    build_dir = 'build/gh-pages/%(BRANCH)s/build'
    t.rm_rf(examples_dir)
    t.makedirs(examples_dir)
    t.rm_rf(build_dir)
    t.makedirs(build_dir)
    t.cp(EXAMPLES, 'examples/examples.css', examples_dir)
    for example in [path.replace('.html', '.js') for path in EXAMPLES]:
        split_example_file(example, examples_dir % vars(variables))
    t.cp_r('examples/data', examples_dir + '/data')
    t.cp_r('examples/bootstrap', examples_dir + '/bootstrap')
    t.cp_r('examples/font-awesome', examples_dir + '/font-awesome')
    t.cp('bin/loader_hosted_examples.js', examples_dir + '/loader.js')
    t.cp('build/ol.js', 'build/ol-simple.js', 'build/ol-whitespace.js',
         'build/ol.css', build_dir)
    t.cp('examples/index.html', 'examples/example-list.js',
         'examples/example-list.xml', 'examples/Jugl.js',
         'examples/jquery.min.js', 'examples/social-links.js', examples_dir)
    t.rm_rf('build/gh-pages/%(BRANCH)s/closure-library')
    t.makedirs('build/gh-pages/%(BRANCH)s/closure-library')
    with t.chdir('build/gh-pages/%(BRANCH)s/closure-library'):
        t.run('%(JAR)s', 'xf', '../../../../' + PLOVR_JAR, 'closure')
        t.run('%(JAR)s', 'xf', '../../../../' + PLOVR_JAR, 'third_party')
    t.rm_rf('build/gh-pages/%(BRANCH)s/ol')
    t.makedirs('build/gh-pages/%(BRANCH)s/ol')
    t.cp_r('src/ol', 'build/gh-pages/%(BRANCH)s/ol/ol')
    t.run('%(PYTHON)s', 'bin/closure/depswriter.py',
          '--root_with_prefix', 'src ../../../ol',
          '--root', 'build/gh-pages/%(BRANCH)s/closure-library/closure/goog',
          '--root_with_prefix', 'build/gh-pages/%(BRANCH)s/closure-library/'
          'third_party ../../third_party',
          '--output_file', 'build/gh-pages/%(BRANCH)s/build/ol-deps.js')


@target('check-examples', 'host-examples', phony=True)
def check_examples(t):
    examples = ['build/gh-pages/%(BRANCH)s/' + e for e in EXAMPLES]
    all_examples = \
        [e + '?mode=raw' for e in examples] + \
        [e + '?mode=whitespace' for e in examples] + \
        [e + '?mode=simple' for e in examples] + \
        examples
    for example in all_examples:
        t.run('%(PHANTOMJS)s', 'bin/check-example.js', example)


@target(PROJ4JS, PROJ4JS_ZIP)
def proj4js(t):
    from zipfile import ZipFile
    zf = ZipFile(PROJ4JS_ZIP)
    contents = zf.open('proj4js/lib/proj4js-combined.js').read()
    with open(t.name, 'wb') as f:
        f.write(contents)


@target(PROJ4JS_ZIP, clean=False)
def proj4js_zip(t):
    t.info('downloading %r', t.name)
    t.download('http://download.osgeo.org/proj4js/' +
               os.path.basename(t.name), md5=PROJ4JS_ZIP_MD5)
    t.info('downloaded %r', t.name)


@target('test', INTERNAL_SRC, PROJ4JS, 'build/test/requireall.js', phony=True)
def test(t):
    t.run('%(PHANTOMJS)s', 'test/mocha-phantomjs.coffee', 'test/ol.html')


@target('fixme', phony=True)
def find_fixme(t):
    regex = re.compile('FIXME|TODO')
    matches = dict()
    totalcount = 0
    for filename in SRC:
        f = open(filename, 'r')
        for lineno, line in enumerate(f):
            if regex.search(line):
                if (filename not in matches):
                    matches[filename] = list()
                matches[filename].append('#%-10d %s' % (
                    lineno + 1, line.strip()))
                totalcount += 1
        f.close()

    for filename in matches:
        num_matches = len(matches[filename])
        noun = 'matches' if num_matches > 1 else 'match'
        print '  %s has %d %s:' % (filename, num_matches, noun)
        for match in matches[filename]:
            print '    %s' % (match,)
        print
    print 'A total of %d TODO/FIXME(s) were found' % (totalcount,)


@target('reallyclean')
def reallyclean(t):
    """Removes untracked files and folders from previous builds."""
    # -X => only clean up files that are usually ignored e.g.
    #       through .gitignore
    # -d => also consider directories for deletion
    # -f => if git configuration variable clean.requireForce != false,
    #       git clean will refuse to run unless given -f or -n.
    t.run('%(GIT)s', 'clean', '-X', '-d', '-f', '.')


if __name__ == '__main__':
    main()
