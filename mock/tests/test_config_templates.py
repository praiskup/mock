from mockbuild.util import TemplatedDictionary


def test_transitive_expand():
    config = TemplatedDictionary()
    config['a'] = 'test'
    config['b'] = '{{ a }} {{ a }}'
    config['c'] = '{{ b + " " + b }}'
    assert config['c'] == '{{ b + " " + b }}'
    config.enable_jinja()
    assert config['c'] == 'test test test test'


def test_aliases():
    config = TemplatedDictionary(
        alias_spec={
            'dnf.conf': ['yum.conf', 'package_manager.conf'],
        },
    )

    config['dnf.conf'] = "initial"
    config['yum.conf'] += " appended"

    config.enable_jinja()
    assert config['package_manager.conf'] == "initial appended"

    config['package_manager.conf'] = "replaced"

    assert config['dnf.conf'] == config['yum.conf'] == 'replaced'

    with config.unexpanded():
        config['variable'] = "content"
        config['package_manager.conf'] += " {{ variable }}"

    assert config['dnf.conf'] == config['yum.conf'] == 'replaced content'

def test_multi_level():
    config = TemplatedDictionary()
    config['plugins'] = {
        'plugin_a': {
            'key': 'value',
            'key2': 'value2',
        },
        'plugin_b': {
            'key': '{{ plugins.plugin_a.key }}',
        },
    }
    config.enable_jinja()
    assert config['plugins']['plugin_a']['key'] == config['plugins']['plugin_b']['key']

    # Try to set also when jinja expanding is enabled, will have no effect
    # because we assign to temporarily created storage, see __render_value()
    # method.
    config['plugins']['plugin_b']['key'] = '{{ plugins.plugin_a.key2 }}'

    assert config['plugins']['plugin_b']['key'] == 'value'  # still plugin_a.key

def test_that_subdict_is_expanded():
    config = TemplatedDictionary()
    config['subdict'] = {}
    config['subdict']['a'] = 'a'
    config['subdict']['b'] = '{{ subdict.a }}'
    config['subdict']['c'] = '{{ a }}'

    config.enable_jinja()

    assert config['subdict']['a'] == config['subdict']['b']

    subdict = config['subdict']
    assert subdict['a'] == subdict['b']

    # we get dict, not TemplatedDictionary() here
    assert type(subdict) == dict

    subconfig = config.copy_subdict('subdict')
    subconfig.enable_jinja()
    assert subconfig['a'] == subconfig['c'] == 'a'

def test_internals():
    config = TemplatedDictionary()
    assert config.__dict__ == {
        '_TemplatedDictionary__aliases': {},
        '_TemplatedDictionary__jinja_expand': False,
    }

def test_that_access_doesnt_affect_value():
    config = TemplatedDictionary()
    config['a'] = {}
    config['a']['b'] = '{{ b }}'
    config.enable_jinja()

    # access it, and check that 'a' isn't changed
    assert '' == config['a']['b']

    # finally set b and check it is still propagated to a.b
    config['b'] = 'b'
    assert 'b' == config['a']['b']
